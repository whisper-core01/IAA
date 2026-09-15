#!/usr/bin/env python3
"""Generate the committed deterministic hotel-planning demonstration."""

from datetime import date, datetime
import json
from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE_ROOT.parent))

from hotel_reservation.planning_view import render_customer_html, render_html, render_svg
from hotel_reservation.reservation_core import GuestProfile, HotelPlanner, ReservationRequest, RestaurantReservation, Room


def at(value: str) -> datetime:
    return datetime.fromisoformat(value)


def build_demo() -> tuple[HotelPlanner, list[dict]]:
    planner = HotelPlanner(
        [
            Room("101", "STANDARD", 75),
            Room("102", "STANDARD", 75),
            Room("201", "DELUXE", 90),
            Room("301", "SUITE", 120),
        ]
    )
    planner.register_guest(GuestProfile("DEMO-GUEST-A", "Client fictif A", date(2000, 9, 20), vip=False))
    planner.register_guest(GuestProfile("DEMO-GUEST-B", "Client fictif B", date(2000, 11, 2), vip=True, preferred_language="fr"))
    planner.register_guest(GuestProfile("DEMO-GUEST-C", "Client fictif C", date(2000, 3, 12)))
    planner.register_guest(GuestProfile("DEMO-GUEST-D", "Client fictif D", date(2000, 6, 8)))
    requests = [
        ReservationRequest("RES-1001", "DEMO-GUEST-A", "STANDARD", at("2026-09-16T15:00:00+02:00"), at("2026-09-18T11:00:00+02:00"), 12000, 12000),
        ReservationRequest("RES-1002", "DEMO-GUEST-B", "STANDARD", at("2026-09-17T15:00:00+02:00"), at("2026-09-19T11:00:00+02:00"), 15000, 15000, vip=True),
        ReservationRequest("RES-1003", "DEMO-GUEST-C", "DELUXE", at("2026-09-18T16:00:00+02:00"), at("2026-09-20T10:00:00+02:00"), 18000, 8000),
        ReservationRequest("RES-1004", "DEMO-GUEST-D", "STANDARD", at("2026-09-18T12:00:00+02:00"), at("2026-09-19T10:00:00+02:00"), 12000, 12000),
    ]
    decisions = [planner.reserve(request).canonical_dict() for request in requests]
    planner.book_restaurant(RestaurantReservation("REST-501", "DEMO-GUEST-B", "Restaurant démo A", at("2026-09-17T20:00:00+02:00"), 120, 2))
    planner.book_restaurant(RestaurantReservation("REST-502", "DEMO-GUEST-B", "Restaurant démo B", at("2026-09-18T12:30:00+02:00"), 90, 3))
    return planner, decisions


def main() -> None:
    planner, decisions = build_demo()
    output = PACKAGE_ROOT / "demo"
    output.mkdir(exist_ok=True)
    start = at("2026-09-16T00:00:00+02:00")
    end = at("2026-09-21T00:00:00+02:00")
    (output / "planning.html").write_text(render_html(planner, start, end), encoding="utf-8")
    (output / "planning.svg").write_text(render_svg(planner, start, end), encoding="utf-8")
    (output / "planning.json").write_text(planner.canonical_json(), encoding="utf-8")
    (output / "decisions.json").write_text(json.dumps(decisions, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "customer-DEMO-GUEST-B.html").write_text(render_customer_html(planner, "DEMO-GUEST-B", date(2026, 9, 15)), encoding="utf-8")
    (output / "customer-DEMO-GUEST-B.json").write_text(json.dumps(planner.customer_record("DEMO-GUEST-B", date(2026, 9, 15)), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
