"""Merge Strava activities (MCP/list_activities shape) into the raw store.

Used by the daily automation (see docs/automation-runbook.md). The scheduled
agent fetches activities via the Strava connection, writes them to a JSON file,
optionally writes a heart-rate map (from get_activity_performance), then runs:

    python etl/merge_strava.py <new_activities.json> [hr_map.json]

- <new_activities.json>: either a raw list or {"activities": [...]} in the
  shape returned by the Strava `list_activities` tool (id, name, sport_type,
  start_local, summary{distance, moving_time, ...}).
- [hr_map.json]: optional {"<activity_id>": {"average_heartrate": x,
  "max_heartrate": y}} from get_activity_performance, to enrich runs with HR.

Merges into data/activities_raw.json deduping by id (new wins). Location is
never stored (ADR-003).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "activities_raw.json"


def to_store_shape(a: dict, hr: dict | None) -> dict:
    s = a.get("summary", a)
    sport = a.get("sport_type", a.get("type", "Unknown"))
    aid = str(a["id"])
    hr_entry = (hr or {}).get(aid, {})
    return {
        "id": int(a["id"]) if str(a["id"]).isdigit() else a["id"],
        "sport_type": sport,
        "type": sport,
        "start_date_local": a.get("start_local") or a.get("start_date_local") or a.get("start_date"),
        "distance": s.get("distance", 0),
        "moving_time": s.get("moving_time", 0),
        "elapsed_time": s.get("elapsed_time", 0),
        "total_elevation_gain": s.get("elevation_gain", s.get("total_elevation_gain", 0)),
        "average_speed": s.get("avg_speed", s.get("average_speed", 0)),
        "max_speed": s.get("max_speed", 0),
        "average_cadence": s.get("avg_cadence", s.get("average_cadence")),
        "calories": s.get("total_calories", s.get("calories", 0)),
        "suffer_score": s.get("relative_effort", s.get("suffer_score")),
        "average_heartrate": hr_entry.get("average_heartrate"),
        "max_heartrate": hr_entry.get("max_heartrate"),
        "name": a.get("name", ""),
        "kudos_count": s.get("kudos_count", 0),
        "pr_count": s.get("pr_count", 0),
        "achievement_count": s.get("achievement_count", 0),
    }


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python etl/merge_strava.py <new_activities.json> [hr_map.json]")
        return 1

    new_raw = json.loads(Path(argv[0]).read_text())
    new_list = new_raw["activities"] if isinstance(new_raw, dict) else new_raw
    hr = json.loads(Path(argv[1]).read_text()) if len(argv) > 1 else None

    store = json.loads(RAW_PATH.read_text()) if RAW_PATH.exists() else []
    by_id = {str(a["id"]): a for a in store}
    added = 0
    for a in new_list:
        shaped = to_store_shape(a, hr)
        if str(shaped["id"]) not in by_id:
            added += 1
        by_id[str(shaped["id"])] = shaped

    merged = sorted(by_id.values(), key=lambda a: a.get("start_date_local") or "")
    RAW_PATH.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    print(f"Store: {len(store)} -> {len(merged)} (+{added} new)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
