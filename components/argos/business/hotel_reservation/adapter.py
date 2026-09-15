"""ARGOS scenario-contract adapter for the hotel reservation component."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from hotel_reservation.reservation_core import (
    GuestProfile,
    HotelPlanner,
    ReservationRequest,
    RestaurantReservation,
    Room,
)


def _datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


class ReservationSession:
    def __init__(self, configuration: dict[str, Any]) -> None:
        self.planner = HotelPlanner(Room(**room) for room in configuration["rooms"])
        for guest in configuration.get("guests", []):
            item = dict(guest)
            item["birth_date"] = date.fromisoformat(item["birth_date"])
            self.planner.register_guest(GuestProfile(**item))

    def handle(self, command: dict[str, Any]) -> dict[str, Any]:
        command_id = command["command_id"]
        operation = command["operation"]
        payload = command.get("payload", {})

        if operation == "hotel.reserve":
            item = dict(payload)
            item["arrival"] = _datetime(item["arrival"])
            item["departure"] = _datetime(item["departure"])
            if "vip" not in item:
                guest = self.planner.guests.get(item["guest_id"])
                item["vip"] = bool(guest and guest.vip)
            result = self.planner.reserve(ReservationRequest(**item)).canonical_dict()
        elif operation == "hotel.cancel":
            result = self.planner.cancel(payload["reservation_id"], _datetime(payload["cancelled_at"])).canonical_dict()
        elif operation == "restaurant.record_reservation":
            item = dict(payload)
            item["start"] = _datetime(item["start"])
            booking = RestaurantReservation(**item)
            self.planner.book_restaurant(booking)
            result = {"decision": "ACCEPTED", "reservation_id": booking.reservation_id}
        elif operation == "hotel.planning":
            result = {"items": self.planner.planning()}
        elif operation == "hotel.customer_record":
            result = self.planner.customer_record(payload["guest_id"], date.fromisoformat(payload["as_of"]))
        else:
            raise ValueError(f"unsupported operation: {operation}")

        return {"command_id": command_id, "operation": operation, "result": result}


def create_session(configuration: dict[str, Any]) -> ReservationSession:
    return ReservationSession(configuration)
