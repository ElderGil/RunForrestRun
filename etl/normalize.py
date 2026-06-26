"""Normalize raw Strava data into the versioned JSON contract (ADR-003).

Emits four files in /data/, each with `schema_version` and `generated_at`:
- activities.json   raw-ish per-activity list (coaches consume this)
- kpis.json         current-month KPIs + guardrail (Hero / Corrida / Força)
- weekly.json       weekly aggregates, last 12 months (evolution chart)
- quarterly.json    per-quarter aggregates since Jun/2024 (Histórico)

Pace is stored as decimal min/km (5:25 -> 5.42). Formatting is the page's job.
No location fields are ever emitted (ADR-003 rule 5).
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SCHEMA_VERSION = "1.0"

# ADR-001: only these sport types are kept.
RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}
STRENGTH_TYPES = {"WeightTraining", "Crossfit", "Workout"}
RIDE_TYPES = {"Ride", "VirtualRide", "MountainBikeRide", "GravelRide", "EBikeRide"}

MONTHS_PT = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
MONTHS_PT_SHORT = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def kind(sport_type: str) -> str | None:
    if sport_type in RUN_TYPES:
        return "Run"
    if sport_type in STRENGTH_TYPES:
        return "Strength"
    if sport_type in RIDE_TYPES:
        return "Ride"
    return None


def parse_date(raw: dict) -> str:
    """Return YYYY-MM-DD. Tolerates the malformed local-time seed format."""
    s = raw.get("start_date_local") or raw.get("start_date") or "2000-01-01"
    return s[:10]


def parse_dt(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def pace_decimal(distance_m: float, moving_s: float) -> float | None:
    """min/km as decimal (e.g. 5:25 -> 5.42). None when not runnable."""
    if not distance_m or distance_m <= 0 or not moving_s:
        return None
    seconds_per_km = moving_s / (distance_m / 1000)
    return round(seconds_per_km / 60, 2)


# --- activities.json ---------------------------------------------------------

def build_activities(raw_list: list[dict]) -> list[dict]:
    out = []
    for raw in raw_list:
        k = kind(raw.get("sport_type", raw.get("type", "")))
        if k is None:
            continue
        dist_m = raw.get("distance", 0) or 0
        moving_s = raw.get("moving_time", 0) or 0
        out.append({
            "id": str(raw["id"]),
            "date": parse_date(raw),
            "type": k,
            "distance_km": round(dist_m / 1000, 2),
            "duration_min": round(moving_s / 60, 1),
            "pace_min_km": pace_decimal(dist_m, moving_s) if k == "Run" else None,
            "avg_heart_rate_bpm": round(raw["average_heartrate"]) if raw.get("average_heartrate") else None,
            "max_heart_rate_bpm": round(raw["max_heartrate"]) if raw.get("max_heartrate") else None,
            "elevation_m": round(raw.get("total_elevation_gain", 0) or 0),
            "name": raw.get("name", ""),
        })
    out.sort(key=lambda a: a["date"])
    return out


# --- weekly.json -------------------------------------------------------------

def week_monday(d: datetime) -> datetime:
    return d - timedelta(days=d.weekday())


def build_weekly(activities: list[dict], months: int = 12) -> list[dict]:
    cutoff = datetime.now() - timedelta(days=months * 30 + 7)
    buckets: dict[str, dict] = defaultdict(lambda: {
        "run_dist": 0.0, "run_pace_sum": 0.0, "run_pace_n": 0,
        "run_sessions": 0, "hr_sum": 0.0, "hr_n": 0, "strength": 0,
    })

    for a in activities:
        d = parse_dt(a["date"])
        if d < cutoff:
            continue
        wk = week_monday(d).strftime("%Y-%m-%d")
        b = buckets[wk]
        if a["type"] == "Run":
            b["run_dist"] += a["distance_km"]
            b["run_sessions"] += 1
            if a["pace_min_km"]:
                b["run_pace_sum"] += a["pace_min_km"]
                b["run_pace_n"] += 1
            if a["avg_heart_rate_bpm"]:
                b["hr_sum"] += a["avg_heart_rate_bpm"]
                b["hr_n"] += 1
        elif a["type"] == "Strength":
            b["strength"] += 1

    weeks = []
    for wk in sorted(buckets):
        b = buckets[wk]
        d = parse_dt(wk)
        weeks.append({
            "week_start": wk,
            "week_label": f"{d.day:02d} {MONTHS_PT_SHORT[d.month]}",
            "running": {
                "distance_km": round(b["run_dist"], 1),
                "avg_pace_min_km": round(b["run_pace_sum"] / b["run_pace_n"], 2) if b["run_pace_n"] else None,
                "sessions": b["run_sessions"],
                "avg_heart_rate_bpm": round(b["hr_sum"] / b["hr_n"]) if b["hr_n"] else None,
            },
            "strength": {"sessions": b["strength"]},
        })
    return weeks


# --- quarterly.json ----------------------------------------------------------

def quarter_of(month: int) -> int:
    return (month - 1) // 3 + 1


def build_quarterly(activities: list[dict]) -> list[dict]:
    buckets: dict[tuple, dict] = defaultdict(lambda: {
        "run_dist": 0.0, "run_pace_sum": 0.0, "run_pace_n": 0,
        "run_sessions": 0, "longest": 0.0, "strength": 0,
    })
    for a in activities:
        d = parse_dt(a["date"])
        key = (d.year, quarter_of(d.month))
        b = buckets[key]
        if a["type"] == "Run":
            b["run_dist"] += a["distance_km"]
            b["run_sessions"] += 1
            b["longest"] = max(b["longest"], a["distance_km"])
            if a["pace_min_km"]:
                b["run_pace_sum"] += a["pace_min_km"]
                b["run_pace_n"] += 1
        elif a["type"] == "Strength":
            b["strength"] += 1

    quarters = []
    for (year, q) in sorted(buckets):
        b = buckets[(year, q)]
        start_month = (q - 1) * 3 + 1
        end_month = start_month + 2
        last_day = (datetime(year + (end_month // 12), (end_month % 12) + 1, 1)
                    - timedelta(days=1)).day
        quarters.append({
            "label": f"Q{q} {year}",
            "period": {
                "start": f"{year}-{start_month:02d}-01",
                "end": f"{year}-{end_month:02d}-{last_day:02d}",
            },
            "running": {
                "total_distance_km": round(b["run_dist"], 1),
                "avg_pace_min_km": round(b["run_pace_sum"] / b["run_pace_n"], 2) if b["run_pace_n"] else None,
                "total_sessions": b["run_sessions"],
                "longest_run_km": round(b["longest"], 1),
            },
            "strength": {"total_sessions": b["strength"]},
        })
    return quarters


# --- kpis.json (current month + guardrail) -----------------------------------

def acute_chronic_ratio(activities: list[dict], ref: datetime) -> dict:
    """ACWR using running distance as load proxy.

    acute   = last 7 days total km
    chronic = avg weekly km over the last 28 days
    """
    runs = [(parse_dt(a["date"]), a["distance_km"]) for a in activities if a["type"] == "Run"]
    acute = sum(km for d, km in runs if (ref - d).days < 7)
    chronic_total = sum(km for d, km in runs if (ref - d).days < 28)
    chronic_weekly = chronic_total / 4 if chronic_total else 0
    ratio = round(acute / chronic_weekly, 2) if chronic_weekly else 0.0

    warning, danger = 1.3, 1.5
    if ratio == 0 or chronic_weekly == 0:
        status = "unknown"
    elif ratio >= danger:
        status = "danger"
    elif ratio >= warning:
        status = "warning"
    else:
        status = "ok"

    return {
        "metric": "acute_chronic_ratio",
        "value": ratio,
        "status": status,
        "threshold_warning": warning,
        "threshold_danger": danger,
        "label": "Razão carga aguda/crônica",
        "description": "Compara o volume da última semana com a média das últimas 4. "
                       "Acima de 1.3 o risco de lesão sobe — o guardrail prioriza saúde sobre velocidade.",
    }


def build_kpis(activities: list[dict]) -> dict:
    ref = datetime.now()
    cur_y, cur_m = ref.year, ref.month
    month_acts = [a for a in activities if a["date"][:7] == f"{cur_y}-{cur_m:02d}"]
    runs = [a for a in month_acts if a["type"] == "Run"]
    strength = [a for a in month_acts if a["type"] == "Strength"]

    # weeks elapsed in current month (for sessions/week)
    weeks_elapsed = max(ref.day / 7, 1)

    paces = [a["pace_min_km"] for a in runs if a["pace_min_km"]]
    hrs = [a["avg_heart_rate_bpm"] for a in runs if a["avg_heart_rate_bpm"]]
    max_hrs = [a["max_heart_rate_bpm"] for a in runs if a["max_heart_rate_bpm"]]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "period": {"month": cur_m, "year": cur_y, "label": f"{MONTHS_PT[cur_m]} {cur_y}"},
        "running": {
            "total_distance_km": round(sum(a["distance_km"] for a in runs), 1),
            "total_sessions": len(runs),
            "avg_pace_min_km": round(sum(paces) / len(paces), 2) if paces else None,
            "avg_heart_rate_bpm": round(sum(hrs) / len(hrs)) if hrs else None,
            "max_heart_rate_bpm": max(max_hrs) if max_hrs else None,
            "total_elevation_m": round(sum(a["elevation_m"] for a in runs)),
            "longest_run_km": round(max((a["distance_km"] for a in runs), default=0), 1),
            "sessions_per_week": round(len(runs) / weeks_elapsed, 1),
            "guardrail": acute_chronic_ratio(activities, ref),
        },
        "strength": {
            "total_sessions": len(strength),
            "sessions_per_week": round(len(strength) / weeks_elapsed, 1),
            "focus": "lower_body",
        },
    }


def wrap(payload, key: str):
    return {"schema_version": SCHEMA_VERSION, "generated_at": now_iso(), key: payload}


def main():
    raw_path = DATA_DIR / "activities_raw.json"
    if not raw_path.exists():
        print("activities_raw.json not found — run strava_fetch.py first")
        return

    raw = json.loads(raw_path.read_text())
    print(f"Loaded {len(raw)} raw activities")

    activities = build_activities(raw)
    weekly = build_weekly(activities)
    quarterly = build_quarterly(activities)
    kpis = build_kpis(activities)

    (DATA_DIR / "activities.json").write_text(
        json.dumps(wrap(activities, "activities"), indent=2, ensure_ascii=False))
    (DATA_DIR / "weekly.json").write_text(
        json.dumps(wrap(weekly, "weeks"), indent=2, ensure_ascii=False))
    (DATA_DIR / "quarterly.json").write_text(
        json.dumps(wrap(quarterly, "quarters"), indent=2, ensure_ascii=False))
    (DATA_DIR / "kpis.json").write_text(
        json.dumps(kpis, indent=2, ensure_ascii=False))

    g = kpis["running"]["guardrail"]
    print("Done.")
    print(f"  Kept activities (Run/Strength/Ride): {len(activities)}")
    print(f"  Weeks (12mo): {len(weekly)} | Quarters: {len(quarterly)}")
    print(f"  Current month: {kpis['period']['label']} — "
          f"{kpis['running']['total_sessions']} runs, {kpis['running']['total_distance_km']} km")
    print(f"  Guardrail ACWR: {g['value']} ({g['status']})")


if __name__ == "__main__":
    main()
