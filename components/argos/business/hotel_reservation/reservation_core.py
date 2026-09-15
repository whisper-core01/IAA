"""Pure, deterministic hotel-reservation rules.

All datetimes must be timezone-aware. Time ranges use half-open intervals:
``[start, end)``. Money is represented as integer cents.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import date, datetime, timedelta
import json
from typing import Iterable


ROOM_TIERS = ("STANDARD", "DELUXE", "SUITE")


def _require_aware(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")


def overlaps(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    """Return whether two half-open time ranges overlap."""
    return start_a < end_b and start_b < end_a


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="minutes")


@dataclass(frozen=True)
class Room:
    room_id: str
    category: str
    cleaning_minutes: int = 90

    def __post_init__(self) -> None:
        if self.category not in ROOM_TIERS:
            raise ValueError(f"unknown room category: {self.category}")
        if self.cleaning_minutes <= 0:
            raise ValueError("cleaning_minutes must be positive")


@dataclass(frozen=True)
class GuestProfile:
    guest_id: str
    display_name: str
    birth_date: date
    vip: bool = False
    preferred_language: str = "fr"
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.guest_id.strip() or not self.display_name.strip():
            raise ValueError("guest_id and display_name are required")


@dataclass(frozen=True)
class RestaurantReservation:
    reservation_id: str
    guest_id: str
    restaurant: str
    start: datetime
    duration_minutes: int
    party_size: int
    status: str = "CONFIRMED"

    def __post_init__(self) -> None:
        _require_aware(self.start, "restaurant start")
        if self.duration_minutes <= 0 or self.party_size <= 0:
            raise ValueError("restaurant duration and party size must be positive")

    @property
    def end(self) -> datetime:
        return self.start + timedelta(minutes=self.duration_minutes)


@dataclass(frozen=True)
class ReservationRequest:
    reservation_id: str
    guest_id: str
    requested_category: str
    arrival: datetime
    departure: datetime
    deposit_required_cents: int
    deposit_paid_cents: int
    vip: bool = False

    def __post_init__(self) -> None:
        if self.requested_category not in ROOM_TIERS:
            raise ValueError(f"unknown room category: {self.requested_category}")
        _require_aware(self.arrival, "arrival")
        _require_aware(self.departure, "departure")
        if self.departure <= self.arrival:
            raise ValueError("departure must be after arrival")
        if self.deposit_required_cents < 0 or self.deposit_paid_cents < 0:
            raise ValueError("deposit amounts cannot be negative")


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    guest_id: str
    room_id: str
    requested_category: str
    assigned_category: str
    arrival: datetime
    departure: datetime
    deposit_cents: int
    vip_upgrade: bool
    status: str = "CONFIRMED"

    @property
    def key_active_from(self) -> datetime:
        return self.arrival

    @property
    def key_active_until(self) -> datetime:
        return self.departure

    @property
    def key_duration_minutes(self) -> int:
        return int((self.key_active_until - self.key_active_from).total_seconds() // 60)


@dataclass(frozen=True)
class Decision:
    decision: str
    reason: str
    reservation: Reservation | None = None
    candidate_room_id: str | None = None
    missing_deposit_cents: int = 0

    def canonical_dict(self) -> dict:
        result = {
            "decision": self.decision,
            "reason": self.reason,
            "candidate_room_id": self.candidate_room_id,
            "missing_deposit_cents": self.missing_deposit_cents,
            "reservation": None,
        }
        if self.reservation:
            item = asdict(self.reservation)
            item["arrival"] = _iso(self.reservation.arrival)
            item["departure"] = _iso(self.reservation.departure)
            item["key_active_from"] = _iso(self.reservation.key_active_from)
            item["key_active_until"] = _iso(self.reservation.key_active_until)
            item["key_duration_minutes"] = self.reservation.key_duration_minutes
            result["reservation"] = item
        return result


@dataclass(frozen=True)
class CancellationDecision:
    decision: str
    reason: str
    reservation_id: str
    cancelled_at: datetime
    refundable_cents: int

    def canonical_dict(self) -> dict:
        result = asdict(self)
        result["cancelled_at"] = _iso(self.cancelled_at)
        return result


class HotelPlanner:
    """In-memory reference engine for the published business rules.

    This implementation demonstrates deterministic rule evaluation. It is not
    a transactional database and must not be used as a production booking or
    physical access-control system.
    """

    def __init__(self, rooms: Iterable[Room]) -> None:
        room_list = sorted(rooms, key=lambda room: room.room_id)
        if not room_list:
            raise ValueError("at least one room is required")
        if len({room.room_id for room in room_list}) != len(room_list):
            raise ValueError("room_id values must be unique")
        self.rooms = {room.room_id: room for room in room_list}
        self.guests: dict[str, GuestProfile] = {}
        self.reservations: dict[str, Reservation] = {}
        self.restaurant_reservations: dict[str, RestaurantReservation] = {}

    def register_guest(self, guest: GuestProfile) -> None:
        if guest.guest_id in self.guests:
            raise ValueError("guest_id values must be unique")
        self.guests[guest.guest_id] = guest

    def book_restaurant(self, reservation: RestaurantReservation) -> None:
        if reservation.guest_id not in self.guests:
            raise ValueError("unknown guest_id")
        if reservation.reservation_id in self.restaurant_reservations:
            raise ValueError("restaurant reservation_id values must be unique")
        self.restaurant_reservations[reservation.reservation_id] = reservation

    def _room_is_free(self, room: Room, arrival: datetime, departure: datetime) -> bool:
        for reservation in self.reservations.values():
            if reservation.room_id != room.room_id or reservation.status != "CONFIRMED":
                continue
            cleaning_end = reservation.departure + timedelta(minutes=room.cleaning_minutes)
            if overlaps(arrival, departure, reservation.arrival, cleaning_end):
                return False
        return True

    def _candidates(self, request: ReservationRequest) -> list[Room]:
        requested_index = ROOM_TIERS.index(request.requested_category)
        category_order = [request.requested_category]
        if request.vip:
            category_order = list(ROOM_TIERS[requested_index + 1 :]) + category_order
        result: list[Room] = []
        for category in category_order:
            result.extend(
                room
                for room in self.rooms.values()
                if room.category == category
                and self._room_is_free(room, request.arrival, request.departure)
            )
        return result

    def reserve(self, request: ReservationRequest) -> Decision:
        if request.guest_id not in self.guests:
            return Decision("REJECTED", "UNKNOWN_GUEST")
        if request.reservation_id in self.reservations:
            return Decision("REJECTED", "DUPLICATE_RESERVATION_ID")

        candidates = self._candidates(request)
        if not candidates:
            return Decision("REJECTED", "NO_ROOM_AVAILABLE")

        room = candidates[0]
        missing = max(0, request.deposit_required_cents - request.deposit_paid_cents)
        if missing:
            return Decision(
                "PENDING_DEPOSIT",
                "DEPOSIT_REQUIRED",
                candidate_room_id=room.room_id,
                missing_deposit_cents=missing,
            )

        reservation = Reservation(
            reservation_id=request.reservation_id,
            guest_id=request.guest_id,
            room_id=room.room_id,
            requested_category=request.requested_category,
            assigned_category=room.category,
            arrival=request.arrival,
            departure=request.departure,
            deposit_cents=request.deposit_paid_cents,
            vip_upgrade=room.category != request.requested_category,
        )
        self.reservations[reservation.reservation_id] = reservation
        return Decision("ACCEPTED", "RESERVATION_CONFIRMED", reservation=reservation)

    def cancel(self, reservation_id: str, cancelled_at: datetime) -> CancellationDecision:
        _require_aware(cancelled_at, "cancelled_at")
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            return CancellationDecision("REJECTED", "UNKNOWN_RESERVATION", reservation_id, cancelled_at, 0)
        if reservation.status != "CONFIRMED":
            return CancellationDecision("REJECTED", "ALREADY_CANCELLED", reservation_id, cancelled_at, 0)

        free_deadline = reservation.arrival - timedelta(hours=48)
        is_free = cancelled_at <= free_deadline
        self.reservations[reservation_id] = replace(reservation, status="CANCELLED")
        return CancellationDecision(
            "ACCEPTED",
            "FREE_CANCELLATION" if is_free else "LATE_CANCELLATION",
            reservation_id,
            cancelled_at,
            reservation.deposit_cents if is_free else 0,
        )

    def planning(self) -> list[dict]:
        items: list[dict] = []
        for reservation in sorted(
            self.reservations.values(), key=lambda item: (item.room_id, item.arrival, item.reservation_id)
        ):
            if reservation.status != "CONFIRMED":
                continue
            room = self.rooms[reservation.room_id]
            cleaning_end = reservation.departure + timedelta(minutes=room.cleaning_minutes)
            items.extend(
                [
                    {
                        "kind": "RESERVATION",
                        "room_id": reservation.room_id,
                        "reservation_id": reservation.reservation_id,
                        "start": _iso(reservation.arrival),
                        "end": _iso(reservation.departure),
                        "duration_minutes": int((reservation.departure - reservation.arrival).total_seconds() // 60),
                    },
                    {
                        "kind": "KEY_ACTIVE",
                        "room_id": reservation.room_id,
                        "reservation_id": reservation.reservation_id,
                        "start": _iso(reservation.key_active_from),
                        "end": _iso(reservation.key_active_until),
                        "duration_minutes": reservation.key_duration_minutes,
                    },
                    {
                        "kind": "CLEANING",
                        "room_id": reservation.room_id,
                        "reservation_id": reservation.reservation_id,
                        "start": _iso(reservation.departure),
                        "end": _iso(cleaning_end),
                        "duration_minutes": room.cleaning_minutes,
                    },
                ]
            )
        return items

    def canonical_json(self) -> str:
        return json.dumps(self.planning(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    def customer_record(self, guest_id: str, as_of: date) -> dict:
        guest = self.guests.get(guest_id)
        if guest is None:
            raise ValueError("unknown guest_id")

        stays = []
        total_minutes = 0
        total_nights = 0
        for reservation in sorted(
            (item for item in self.reservations.values() if item.guest_id == guest_id),
            key=lambda item: (item.arrival, item.reservation_id),
        ):
            duration_minutes = int((reservation.departure - reservation.arrival).total_seconds() // 60)
            nights = max(1, (reservation.departure.date() - reservation.arrival.date()).days)
            if reservation.status == "CONFIRMED":
                total_minutes += duration_minutes
                total_nights += nights
            stays.append({
                "reservation_id": reservation.reservation_id,
                "room_id": reservation.room_id,
                "arrival": _iso(reservation.arrival),
                "departure": _iso(reservation.departure),
                "duration_minutes": duration_minutes,
                "nights": nights,
                "status": reservation.status,
            })

        restaurants = []
        for booking in sorted(
            (item for item in self.restaurant_reservations.values() if item.guest_id == guest_id),
            key=lambda item: (item.start, item.reservation_id),
        ):
            restaurants.append({
                "reservation_id": booking.reservation_id,
                "restaurant": booking.restaurant,
                "start": _iso(booking.start),
                "end": _iso(booking.end),
                "duration_minutes": booking.duration_minutes,
                "party_size": booking.party_size,
                "status": booking.status,
            })

        try:
            birthday = guest.birth_date.replace(year=as_of.year)
        except ValueError:  # 29 February in a non-leap year
            birthday = date(as_of.year, 2, 28)
        if birthday < as_of:
            try:
                birthday = birthday.replace(year=as_of.year + 1)
            except ValueError:  # 29 February in a non-leap year
                birthday = date(as_of.year + 1, 2, 28)

        return {
            "guest_id": guest.guest_id,
            "display_name": guest.display_name,
            "birth_date": guest.birth_date.isoformat(),
            "next_birthday": birthday.isoformat(),
            "vip": guest.vip,
            "preferred_language": guest.preferred_language,
            "notes": guest.notes,
            "hotel_reservation_count": len(stays),
            "total_confirmed_stay_minutes": total_minutes,
            "total_confirmed_nights": total_nights,
            "restaurant_reservation_count": len(restaurants),
            "hotel_history": stays,
            "restaurant_history": restaurants,
        }
