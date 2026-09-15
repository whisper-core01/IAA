"""Dependency-free HTML and SVG planning views."""

from __future__ import annotations

from datetime import date, datetime
from html import escape

from .reservation_core import HotelPlanner


COLORS = {"RESERVATION": "#2563eb", "CLEANING": "#f59e0b", "KEY_ACTIVE": "#16a34a"}
LABELS = {"RESERVATION": "Réservation", "CLEANING": "Nettoyage", "KEY_ACTIVE": "Clé active"}


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _position(value: datetime, start: datetime, end: datetime) -> float:
    return 100 * (value - start).total_seconds() / (end - start).total_seconds()


def _events(planner: HotelPlanner, start: datetime, end: datetime) -> list[dict]:
    result = []
    for item in planner.planning():
        item_start, item_end = _parse(item["start"]), _parse(item["end"])
        if item_start < end and start < item_end:
            copied = dict(item)
            copied["left"] = max(0.0, _position(max(start, item_start), start, end))
            copied["right"] = min(100.0, _position(min(end, item_end), start, end))
            result.append(copied)
    return result


def render_html(planner: HotelPlanner, start: datetime, end: datetime) -> str:
    events = _events(planner, start, end)
    lanes = []
    details = []
    for room in planner.rooms.values():
        blocks = []
        for item in events:
            if item["room_id"] != room.room_id:
                continue
            width = max(0.35, item["right"] - item["left"])
            top = {"RESERVATION": 5, "KEY_ACTIVE": 37, "CLEANING": 69}[item["kind"]]
            title = (
                f'{LABELS[item["kind"]]} · {item["reservation_id"]} · '
                f'{item["start"]} → {item["end"]} · {item["duration_minutes"]} min'
            )
            blocks.append(
                f'<div class="event {item["kind"].lower()}" '
                f'style="left:{item["left"]:.4f}%;width:{width:.4f}%;top:{top}px" '
                f'title="{escape(title)}">{escape(item["reservation_id"])}</div>'
            )
            details.append(
                "<tr>"
                f"<td>{escape(room.room_id)}</td><td>{escape(LABELS[item['kind']])}</td>"
                f"<td>{escape(item['reservation_id'])}</td><td>{escape(item['start'])}</td>"
                f"<td>{escape(item['end'])}</td><td>{item['duration_minutes']} min</td>"
                "</tr>"
            )
        lanes.append(
            f'<div class="room-label"><strong>{escape(room.room_id)}</strong><small>{escape(room.category)}</small></div>'
            f'<div class="lane">{"".join(blocks)}</div>'
        )

    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IAA — Planning hôtelier</title><style>
:root{{--bg:#08111f;--panel:#111d31;--line:#29405f;--text:#e7eef9;--muted:#9fb0c8}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:14px system-ui,sans-serif}}
main{{max-width:1280px;margin:auto;padding:28px}} h1{{margin:0 0 4px;font-size:28px}} p{{color:var(--muted)}}
.legend{{display:flex;gap:18px;margin:20px 0}} .swatch{{width:12px;height:12px;display:inline-block;border-radius:3px;margin-right:6px}}
.grid{{display:grid;grid-template-columns:120px 1fr;border:1px solid var(--line);border-radius:10px;overflow:hidden}}
.room-label{{padding:16px;background:var(--panel);border-bottom:1px solid var(--line)}} .room-label small{{display:block;color:var(--muted)}}
.lane{{height:100px;position:relative;border-bottom:1px solid var(--line);background:repeating-linear-gradient(90deg,transparent 0,transparent calc(12.5% - 1px),var(--line) 12.5%)}}
.event{{position:absolute;height:25px;border-radius:5px;padding:4px 7px;overflow:hidden;white-space:nowrap;font-size:12px;font-weight:650}}
.reservation{{background:{COLORS['RESERVATION']}}}.cleaning{{background:{COLORS['CLEANING']};color:#241400}}.key_active{{background:{COLORS['KEY_ACTIVE']}}}
table{{width:100%;border-collapse:collapse;margin-top:24px;background:var(--panel)}} th,td{{padding:9px;border:1px solid var(--line);text-align:left}} th{{color:var(--muted)}}
</style></head><body><main><h1>Planning hôtelier IAA</h1>
<p>Fenêtre : {escape(start.isoformat(timespec='minutes'))} → {escape(end.isoformat(timespec='minutes'))}</p>
<div class="legend"><span><i class="swatch" style="background:{COLORS['RESERVATION']}"></i>Réservation</span><span><i class="swatch" style="background:{COLORS['CLEANING']}"></i>Nettoyage</span><span><i class="swatch" style="background:{COLORS['KEY_ACTIVE']}"></i>Clé magnétique active</span></div>
<div class="grid">{''.join(lanes)}</div>
<table><thead><tr><th>Chambre</th><th>Type</th><th>Réservation</th><th>Début</th><th>Fin</th><th>Durée</th></tr></thead><tbody>{''.join(details)}</tbody></table>
</main></body></html>\n"""


def render_svg(planner: HotelPlanner, start: datetime, end: datetime) -> str:
    events = _events(planner, start, end)
    rooms = list(planner.rooms.values())
    width, label_width, chart_width = 1280, 150, 1080
    height = 120 + 100 * len(rooms)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#08111f"/>',
        '<style>text{font-family:system-ui,sans-serif;fill:#e7eef9}.muted{fill:#9fb0c8}.id{font-size:11px;font-weight:650}</style>',
        '<text x="30" y="38" font-size="26" font-weight="700">Planning hôtelier IAA</text>',
        f'<text class="muted" x="30" y="64" font-size="13">{escape(start.isoformat(timespec="minutes"))} → {escape(end.isoformat(timespec="minutes"))}</text>',
    ]
    for index, room in enumerate(rooms):
        y = 90 + index * 100
        parts.extend([
            f'<rect x="20" y="{y}" width="1240" height="88" rx="7" fill="#111d31" stroke="#29405f"/>',
            f'<text x="35" y="{y + 33}" font-size="16" font-weight="700">{escape(room.room_id)}</text>',
            f'<text class="muted" x="35" y="{y + 54}" font-size="11">{escape(room.category)}</text>',
        ])
        for tick in range(9):
            x = label_width + chart_width * tick / 8
            parts.append(f'<line x1="{x:.1f}" y1="{y}" x2="{x:.1f}" y2="{y + 88}" stroke="#29405f"/>')
        for item in events:
            if item["room_id"] != room.room_id:
                continue
            x = label_width + chart_width * item["left"] / 100
            event_width = max(4, chart_width * (item["right"] - item["left"]) / 100)
            offset = {"RESERVATION": 7, "KEY_ACTIVE": 34, "CLEANING": 61}[item["kind"]]
            parts.append(f'<rect x="{x:.1f}" y="{y + offset}" width="{event_width:.1f}" height="20" rx="4" fill="{COLORS[item["kind"]]}"/>')
            if event_width > 45:
                parts.append(f'<text class="id" x="{x + 5:.1f}" y="{y + offset + 14}">{escape(item["reservation_id"])}</text>')
    parts.append('</svg>\n')
    return "".join(parts)


def render_customer_html(planner: HotelPlanner, guest_id: str, as_of: date) -> str:
    record = planner.customer_record(guest_id, as_of)
    stays = "".join(
        "<tr>"
        f"<td>{escape(item['reservation_id'])}</td><td>{escape(item['room_id'])}</td>"
        f"<td>{escape(item['arrival'])}</td><td>{escape(item['departure'])}</td>"
        f"<td>{item['nights']}</td><td>{item['duration_minutes']} min</td><td>{escape(item['status'])}</td>"
        "</tr>"
        for item in record["hotel_history"]
    )
    restaurants = "".join(
        "<tr>"
        f"<td>{escape(item['reservation_id'])}</td><td>{escape(item['restaurant'])}</td>"
        f"<td>{escape(item['start'])}</td><td>{item['duration_minutes']} min</td>"
        f"<td>{item['party_size']}</td><td>{escape(item['status'])}</td>"
        "</tr>"
        for item in record["restaurant_history"]
    )
    vip = "VIP" if record["vip"] else "Standard"
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fiche client — {escape(record['display_name'])}</title><style>
:root{{--bg:#08111f;--panel:#111d31;--line:#29405f;--text:#e7eef9;--muted:#9fb0c8;--accent:#60a5fa}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px system-ui,sans-serif}}main{{max-width:1100px;margin:auto;padding:28px}}
.profile{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:14px}}.card span{{display:block;color:var(--muted);font-size:12px}}.card strong{{font-size:17px;color:var(--accent)}}
table{{width:100%;border-collapse:collapse;margin:12px 0 28px;background:var(--panel)}}th,td{{padding:9px;border:1px solid var(--line);text-align:left}}th{{color:var(--muted)}}h2{{margin-top:28px}}
</style></head><body><main><h1>{escape(record['display_name'])}</h1><p>{escape(vip)} · Langue : {escape(record['preferred_language'])}</p>
<div class="profile"><div class="card"><span>Date de naissance</span><strong>{record['birth_date']}</strong></div><div class="card"><span>Prochain anniversaire</span><strong>{record['next_birthday']}</strong></div><div class="card"><span>Nuits confirmées</span><strong>{record['total_confirmed_nights']}</strong></div><div class="card"><span>Durée cumulée</span><strong>{record['total_confirmed_stay_minutes']} min</strong></div></div>
<h2>Historique des séjours</h2><table><thead><tr><th>Réservation</th><th>Chambre</th><th>Arrivée</th><th>Départ</th><th>Nuits</th><th>Durée</th><th>Statut</th></tr></thead><tbody>{stays}</tbody></table>
<h2>Réservations restaurant</h2><table><thead><tr><th>Réservation</th><th>Restaurant</th><th>Date</th><th>Durée</th><th>Couverts</th><th>Statut</th></tr></thead><tbody>{restaurants}</tbody></table>
</main></body></html>\n"""
