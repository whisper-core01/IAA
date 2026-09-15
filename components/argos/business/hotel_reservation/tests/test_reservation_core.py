from datetime import date, datetime
from pathlib import Path
import sys
import unittest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT.parent))

from hotel_reservation.planning_view import render_customer_html, render_html
from hotel_reservation.reservation_core import GuestProfile, HotelPlanner, ReservationRequest, RestaurantReservation, Room, overlaps


def at(value: str) -> datetime:
    return datetime.fromisoformat(value)


class ReservationRulesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = HotelPlanner([
            Room("101", "STANDARD", 75),
            Room("201", "DELUXE", 90),
            Room("301", "SUITE", 120),
        ])
        self.planner.register_guest(GuestProfile("GUEST-1", "Client test", date(2000, 9, 20), vip=True))

    def request(self, reservation_id="RES-1", category="STANDARD", paid=12000, vip=False,
                arrival="2026-09-16T15:00:00+02:00", departure="2026-09-18T11:00:00+02:00"):
        return ReservationRequest(reservation_id, "GUEST-1", category, at(arrival), at(departure), 12000, paid, vip)

    def test_half_open_ranges_allow_touching_boundaries(self):
        start = at("2026-09-16T10:00:00+02:00")
        middle = at("2026-09-16T11:00:00+02:00")
        end = at("2026-09-16T12:00:00+02:00")
        self.assertFalse(overlaps(start, middle, middle, end))

    def test_deposit_is_required_and_no_key_is_created(self):
        decision = self.planner.reserve(self.request(paid=5000))
        self.assertEqual("PENDING_DEPOSIT", decision.decision)
        self.assertEqual(7000, decision.missing_deposit_cents)
        self.assertEqual([], self.planner.planning())

    def test_confirmed_reservation_creates_key_and_cleaning(self):
        decision = self.planner.reserve(self.request())
        self.assertEqual("ACCEPTED", decision.decision)
        items = self.planner.planning()
        self.assertEqual(["RESERVATION", "KEY_ACTIVE", "CLEANING"], [item["kind"] for item in items])
        key = items[1]
        cleaning = items[2]
        self.assertEqual(2640, key["duration_minutes"])
        self.assertEqual("2026-09-16T15:00+02:00", key["start"])
        self.assertEqual("2026-09-18T11:00+02:00", key["end"])
        self.assertEqual(75, cleaning["duration_minutes"])
        self.assertEqual("2026-09-18T12:15+02:00", cleaning["end"])

    def test_cleaning_window_blocks_early_next_arrival(self):
        self.planner.reserve(self.request())
        rejected = self.planner.reserve(self.request(
            reservation_id="RES-2",
            arrival="2026-09-18T11:30:00+02:00",
            departure="2026-09-19T10:00:00+02:00",
        ))
        self.assertEqual("REJECTED", rejected.decision)
        self.assertEqual("NO_ROOM_AVAILABLE", rejected.reason)

    def test_arrival_at_cleaning_end_is_allowed(self):
        one_room = HotelPlanner([Room("101", "STANDARD", 75)])
        one_room.register_guest(GuestProfile("GUEST-1", "Client test", date(2000, 9, 20)))
        one_room.reserve(self.request())
        decision = one_room.reserve(self.request(
            reservation_id="RES-2",
            arrival="2026-09-18T12:15:00+02:00",
            departure="2026-09-19T10:00:00+02:00",
        ))
        self.assertEqual("ACCEPTED", decision.decision)

    def test_vip_is_upgraded_to_next_available_tier(self):
        decision = self.planner.reserve(self.request(vip=True))
        self.assertEqual("DELUXE", decision.reservation.assigned_category)
        self.assertTrue(decision.reservation.vip_upgrade)

    def test_vip_falls_back_to_requested_category(self):
        self.planner.reserve(self.request(reservation_id="D", category="DELUXE"))
        self.planner.reserve(self.request(reservation_id="S", category="SUITE"))
        vip = self.planner.reserve(self.request(reservation_id="VIP", vip=True))
        self.assertEqual("STANDARD", vip.reservation.assigned_category)
        self.assertFalse(vip.reservation.vip_upgrade)

    def test_duplicate_identifier_is_rejected(self):
        self.planner.reserve(self.request())
        decision = self.planner.reserve(self.request())
        self.assertEqual("DUPLICATE_RESERVATION_ID", decision.reason)

    def test_free_cancellation_at_exact_48_hour_boundary(self):
        self.planner.reserve(self.request())
        cancelled = self.planner.cancel("RES-1", at("2026-09-14T15:00:00+02:00"))
        self.assertEqual("FREE_CANCELLATION", cancelled.reason)
        self.assertEqual(12000, cancelled.refundable_cents)
        self.assertEqual([], self.planner.planning())

    def test_late_cancellation_retains_deposit(self):
        self.planner.reserve(self.request())
        cancelled = self.planner.cancel("RES-1", at("2026-09-14T15:01:00+02:00"))
        self.assertEqual("LATE_CANCELLATION", cancelled.reason)
        self.assertEqual(0, cancelled.refundable_cents)

    def test_naive_datetime_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            ReservationRequest("R", "G", "STANDARD", datetime(2026, 9, 16), at("2026-09-17T10:00:00+02:00"), 1, 1)

    def test_unknown_guest_is_rejected(self):
        request = ReservationRequest("R", "UNKNOWN", "STANDARD", at("2026-09-16T15:00:00+02:00"), at("2026-09-17T10:00:00+02:00"), 1, 1)
        self.assertEqual("UNKNOWN_GUEST", self.planner.reserve(request).reason)

    def test_customer_record_contains_stay_restaurant_and_birthday(self):
        self.planner.reserve(self.request())
        self.planner.book_restaurant(RestaurantReservation("REST-1", "GUEST-1", "Restaurant test", at("2026-09-17T20:00:00+02:00"), 120, 2))
        record = self.planner.customer_record("GUEST-1", date(2026, 9, 15))
        self.assertEqual("2026-09-20", record["next_birthday"])
        self.assertEqual(2, record["total_confirmed_nights"])
        self.assertEqual(2640, record["total_confirmed_stay_minutes"])
        self.assertEqual("Restaurant test", record["restaurant_history"][0]["restaurant"])
        html = render_customer_html(self.planner, "GUEST-1", date(2026, 9, 15))
        self.assertIn("Historique des séjours", html)
        self.assertIn("Réservations restaurant", html)

    def test_leap_day_birthday_has_deterministic_non_leap_policy(self):
        self.planner.register_guest(GuestProfile("LEAP", "Client test bissextile", date(2000, 2, 29)))
        record = self.planner.customer_record("LEAP", date(2027, 1, 10))
        self.assertEqual("2027-02-28", record["next_birthday"])

    def test_html_contains_exact_key_dates_and_duration(self):
        self.planner.reserve(self.request())
        html = render_html(self.planner, at("2026-09-16T00:00:00+02:00"), at("2026-09-19T00:00:00+02:00"))
        self.assertIn("Clé magnétique active", html)
        self.assertIn("2026-09-16T15:00+02:00", html)
        self.assertIn("2640 min", html)

    def test_invalid_room_and_stay_data_are_rejected(self):
        with self.assertRaises(ValueError):
            Room("X", "UNKNOWN")
        with self.assertRaises(ValueError):
            self.request(arrival="2026-09-18T11:00:00+02:00", departure="2026-09-18T11:00:00+02:00")


if __name__ == "__main__":
    unittest.main()
