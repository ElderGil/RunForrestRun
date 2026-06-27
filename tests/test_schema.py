"""Contract tests for the generated JSON files (ADR-003).

Validates the data currently in /data so a broken ETL output never ships.
"""

import json
from pathlib import Path

import pytest

DATA = Path(__file__).parent.parent / "data"

LOCATION_FIELDS = {"lat", "lng", "start_latlng", "end_latlng", "map"}


def load(name):
    return json.loads((DATA / name).read_text())


@pytest.mark.parametrize("name", ["kpis.json", "weekly.json", "quarterly.json", "monthly.json", "activities.json"])
def test_has_version_and_timestamp(name):
    d = load(name)
    assert d["schema_version"] == "1.0"
    assert d["generated_at"].endswith("Z")


def test_kpis_shape():
    d = load("kpis.json")
    assert {"month", "year", "label"} <= d["period"].keys()
    r = d["running"]
    for k in ("total_distance_km", "total_sessions", "longest_run_km", "sessions_per_week", "guardrail"):
        assert k in r
    g = r["guardrail"]
    assert g["metric"] == "acute_chronic_ratio"
    assert g["status"] in {"ok", "warning", "danger", "unknown"}
    assert g["threshold_warning"] < g["threshold_danger"]
    assert {"total_sessions", "focus"} <= d["strength"].keys()


def test_weekly_shape_and_pace_is_decimal():
    weeks = load("weekly.json")["weeks"]
    assert len(weeks) > 0
    for w in weeks:
        assert "week_start" in w and "week_label" in w
        pace = w["running"]["avg_pace_min_km"]
        assert pace is None or isinstance(pace, (int, float))
        # pace decimal, nunca string "5:25"
        assert not isinstance(pace, str)


def test_monthly_shape():
    months = load("monthly.json")["months"]
    for m in months:
        assert m["month"].startswith("2026-")
        assert "label" in m and "run_km" in m and "longest_run_km" in m
        pace = m["avg_pace_min_km"]
        assert pace is None or isinstance(pace, (int, float))


def test_quarterly_chronological_labels():
    quarters = load("quarterly.json")["quarters"]
    assert len(quarters) > 0
    for q in quarters:
        assert q["label"].startswith("Q")
        assert {"start", "end"} <= q["period"].keys()


def test_activities_have_no_location():
    acts = load("activities.json")["activities"]
    assert len(acts) > 0
    for a in acts:
        assert not (LOCATION_FIELDS & a.keys()), f"location leak in {a['id']}"
        assert a["type"] in {"Run", "Strength", "Ride"}


def test_weekly_plan_shape_if_present():
    path = DATA / "weekly_plan.json"
    if not path.exists():
        pytest.skip("weekly_plan.json ainda não gerado")
    d = json.loads(path.read_text())
    assert d["schema_version"] in {"1.0", "2.0"}
    assert len(d["days"]) == 7
    valid = {"run", "strength", "rest"}
    for day in d["days"]:
        for item in day["items"]:
            assert item["type"] in valid
