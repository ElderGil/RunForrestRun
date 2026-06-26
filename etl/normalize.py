"""Normalize raw Strava data into KPI JSONs consumed by the site."""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

SPORT_GROUPS = {
    "Run": ["Run", "TrailRun", "VirtualRun"],
    "Ride": ["Ride", "VirtualRide", "MountainBikeRide", "GravelRide", "EBikeRide"],
    "Strength": ["WeightTraining", "Crossfit", "Workout"],
    "Walk": ["Walk", "Hike"],
}

HR_ZONES = [
    {"label": "Z1 Recovery", "min": 0, "max": 118},
    {"label": "Z2 Aerobic", "min": 119, "max": 147},
    {"label": "Z3 Tempo", "min": 148, "max": 162},
    {"label": "Z4 Threshold", "min": 163, "max": 177},
    {"label": "Z5 VO2max", "min": 178, "max": 999},
]


def sport_group(sport_type: str) -> str:
    for group, types in SPORT_GROUPS.items():
        if sport_type in types:
            return group
    return "Other"


def pace_str(avg_speed_ms: float) -> str:
    """Convert m/s to min/km string."""
    if not avg_speed_ms or avg_speed_ms <= 0:
        return None
    seconds_per_km = 1000 / avg_speed_ms
    m, s = divmod(int(seconds_per_km), 60)
    return f"{m}:{s:02d}"


def pace_seconds(avg_speed_ms: float) -> float:
    if not avg_speed_ms or avg_speed_ms <= 0:
        return None
    return 1000 / avg_speed_ms


def iso_week(date_str: str) -> str:
    """Return ISO week label like '2025-W23'."""
    dt = datetime.fromisoformat(date_str[:10])
    return dt.strftime("%G-W%V")


def iso_month(date_str: str) -> str:
    return date_str[:7]


def normalize_activity(raw: dict) -> dict:
    sport = raw.get("sport_type", raw.get("type", "Unknown"))
    group = sport_group(sport)
    distance_km = raw.get("distance", 0) / 1000
    moving_s = raw.get("moving_time", 0)
    avg_speed = raw.get("average_speed", 0)

    act = {
        "id": raw["id"],
        "name": raw.get("name", ""),
        "sport_type": sport,
        "sport_group": group,
        "start_date": raw.get("start_date_local", raw.get("start_date", "")),
        "distance_km": round(distance_km, 3),
        "moving_time_s": moving_s,
        "elapsed_time_s": raw.get("elapsed_time", 0),
        "elevation_gain_m": raw.get("total_elevation_gain", 0),
        "avg_speed_ms": avg_speed,
        "max_speed_ms": raw.get("max_speed", 0),
        "avg_hr": raw.get("average_heartrate"),
        "max_hr": raw.get("max_heartrate"),
        "avg_cadence": raw.get("average_cadence"),
        "calories": raw.get("calories", raw.get("kilojoules", 0)),
        "suffer_score": raw.get("suffer_score"),
        "kudos": raw.get("kudos_count", 0),
        "pr_count": raw.get("pr_count", 0),
        "achievement_count": raw.get("achievement_count", 0),
        "week": iso_week(raw.get("start_date_local", raw.get("start_date", "2000-01-01"))),
        "month": iso_month(raw.get("start_date_local", raw.get("start_date", "2000-01-01"))),
    }

    if group == "Run" and avg_speed > 0:
        act["pace_str"] = pace_str(avg_speed)
        act["pace_s_per_km"] = round(pace_seconds(avg_speed), 1)

    return act


def build_weekly(activities: list[dict]) -> list[dict]:
    weeks: dict[str, dict] = defaultdict(lambda: {
        "run_km": 0, "run_count": 0, "ride_km": 0, "strength_count": 0,
        "walk_km": 0, "other_count": 0, "total_elevation_m": 0,
        "avg_pace_s_sum": 0, "avg_pace_s_count": 0,
    })

    for a in activities:
        w = weeks[a["week"]]
        g = a["sport_group"]
        if g == "Run":
            w["run_km"] += a["distance_km"]
            w["run_count"] += 1
            if a.get("pace_s_per_km"):
                w["avg_pace_s_sum"] += a["pace_s_per_km"]
                w["avg_pace_s_count"] += 1
        elif g == "Ride":
            w["ride_km"] += a["distance_km"]
        elif g == "Strength":
            w["strength_count"] += 1
        elif g == "Walk":
            w["walk_km"] += a["distance_km"]
        else:
            w["other_count"] += 1
        w["total_elevation_m"] += a["elevation_gain_m"]

    result = []
    for week, data in sorted(weeks.items()):
        avg_pace_s = None
        if data["avg_pace_s_count"] > 0:
            avg_pace_s = round(data["avg_pace_s_sum"] / data["avg_pace_s_count"], 1)
            m, s = divmod(int(avg_pace_s), 60)
            avg_pace_str = f"{m}:{s:02d}"
        else:
            avg_pace_str = None

        result.append({
            "week": week,
            "run_km": round(data["run_km"], 2),
            "run_count": data["run_count"],
            "ride_km": round(data["ride_km"], 2),
            "strength_count": data["strength_count"],
            "walk_km": round(data["walk_km"], 2),
            "other_count": data["other_count"],
            "total_elevation_m": round(data["total_elevation_m"], 1),
            "avg_pace_s_per_km": avg_pace_s,
            "avg_pace_str": avg_pace_str,
        })

    return result


def build_monthly(activities: list[dict]) -> list[dict]:
    months: dict[str, dict] = defaultdict(lambda: {
        "run_km": 0, "run_count": 0, "ride_km": 0, "strength_count": 0,
        "total_elevation_m": 0, "long_run_km": 0,
        "avg_hr_sum": 0, "avg_hr_count": 0,
    })

    for a in activities:
        m = months[a["month"]]
        g = a["sport_group"]
        if g == "Run":
            m["run_km"] += a["distance_km"]
            m["run_count"] += 1
            if a["distance_km"] > m["long_run_km"]:
                m["long_run_km"] = a["distance_km"]
        elif g == "Ride":
            m["ride_km"] += a["distance_km"]
        elif g == "Strength":
            m["strength_count"] += 1
        m["total_elevation_m"] += a["elevation_gain_m"]
        if a.get("avg_hr"):
            m["avg_hr_sum"] += a["avg_hr"]
            m["avg_hr_count"] += 1

    result = []
    for month, data in sorted(months.items()):
        avg_hr = round(data["avg_hr_sum"] / data["avg_hr_count"], 1) if data["avg_hr_count"] else None
        result.append({
            "month": month,
            "run_km": round(data["run_km"], 2),
            "run_count": data["run_count"],
            "ride_km": round(data["ride_km"], 2),
            "strength_count": data["strength_count"],
            "total_elevation_m": round(data["total_elevation_m"], 1),
            "long_run_km": round(data["long_run_km"], 2),
            "avg_hr": avg_hr,
        })

    return result


def build_kpis(activities: list[dict], weekly: list[dict], monthly: list[dict]) -> dict:
    runs = [a for a in activities if a["sport_group"] == "Run"]

    # Last 4 weeks
    recent_weeks = weekly[-4:] if len(weekly) >= 4 else weekly
    recent_run_km = sum(w["run_km"] for w in recent_weeks)
    avg_weekly_km = round(recent_run_km / len(recent_weeks), 2) if recent_weeks else 0

    # Best long run ever
    long_run_km = max((a["distance_km"] for a in runs), default=0)

    # Recent pace (last 5 runs)
    recent_runs = sorted(runs, key=lambda a: a["start_date"], reverse=True)[:5]
    paces = [a["pace_s_per_km"] for a in recent_runs if a.get("pace_s_per_km")]
    avg_pace_s = round(sum(paces) / len(paces), 1) if paces else None
    if avg_pace_s:
        m, s = divmod(int(avg_pace_s), 60)
        avg_pace_str = f"{m}:{s:02d}"
    else:
        avg_pace_str = None

    # Consistency: weeks with at least 1 run, in last 12 weeks
    last_12 = weekly[-12:] if len(weekly) >= 12 else weekly
    active_weeks = sum(1 for w in last_12 if w["run_count"] > 0)
    consistency_pct = round(active_weeks / len(last_12) * 100) if last_12 else 0

    # Total ever
    total_run_km = round(sum(a["distance_km"] for a in runs), 2)
    total_runs = len(runs)

    return {
        "as_of": datetime.now().isoformat(timespec="seconds"),
        "avg_weekly_run_km": avg_weekly_km,
        "avg_pace_str": avg_pace_str,
        "avg_pace_s_per_km": avg_pace_s,
        "long_run_km": round(long_run_km, 2),
        "consistency_pct_12w": consistency_pct,
        "active_weeks_of_12": active_weeks,
        "total_run_km": total_run_km,
        "total_run_count": total_runs,
        "goal_half_marathon": {
            "event": "Meia Maratona Pomerode",
            "date": "2026-10-17",
            "distance_km": 21.1,
        },
        "goal_marathon": {
            "event": "Maratona",
            "date": "2027-12-31",
            "distance_km": 42.2,
        },
    }


def main():
    raw_path = DATA_DIR / "activities_raw.json"
    if not raw_path.exists():
        print("activities_raw.json not found — run strava_fetch.py first")
        return

    print("Loading raw activities...")
    raw = json.loads(raw_path.read_text())
    print(f"  {len(raw)} raw activities")

    print("Normalizing activities...")
    activities = [normalize_activity(a) for a in raw]
    (DATA_DIR / "activities.json").write_text(json.dumps(activities, indent=2))

    print("Building weekly summaries...")
    weekly = build_weekly(activities)
    (DATA_DIR / "weekly.json").write_text(json.dumps(weekly, indent=2))

    print("Building monthly summaries...")
    monthly = build_monthly(activities)
    (DATA_DIR / "monthly.json").write_text(json.dumps(monthly, indent=2))

    print("Calculating KPIs...")
    kpis = build_kpis(activities, weekly, monthly)
    (DATA_DIR / "kpis.json").write_text(json.dumps(kpis, indent=2))

    print("Done.")
    print(f"  Activities: {len(activities)}")
    print(f"  Weeks: {len(weekly)}")
    print(f"  Months: {len(monthly)}")
    print(f"  Avg weekly km (last 4w): {kpis['avg_weekly_run_km']}")
    print(f"  Avg pace (last 5 runs): {kpis['avg_pace_str']}")
    print(f"  Long run: {kpis['long_run_km']} km")
    print(f"  Consistency (12w): {kpis['consistency_pct_12w']}%")


if __name__ == "__main__":
    main()
