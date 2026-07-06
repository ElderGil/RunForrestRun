"""Unit tests for the ETL normalization logic (etl/normalize.py)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "etl"))

import normalize as N  # noqa: E402


def test_kind_maps_sport_types():
    assert N.kind("Run") == "Run"
    assert N.kind("TrailRun") == "Run"
    assert N.kind("WeightTraining") == "Strength"
    assert N.kind("Ride") == "Ride"
    assert N.kind("Walk") is None  # Walk is dropped per ADR-001
    assert N.kind("Yoga") is None


def test_pace_decimal():
    # 1000 m em 325 s => 5:25/km => 5.42 decimal
    assert N.pace_decimal(1000, 325) == 5.42
    # sem distância/tempo => None
    assert N.pace_decimal(0, 600) is None
    assert N.pace_decimal(1000, 0) is None


def test_parse_date_tolerates_seed_format():
    assert N.parse_date({"start_date_local": "2026-06-23T07:45:10:00"}) == "2026-06-23"
    assert N.parse_date({"start_date": "2025-01-02T00:00:00Z"}) == "2025-01-02"


def test_build_activities_filters_and_shapes():
    raw = [
        {"id": 1, "sport_type": "Run", "start_date_local": "2026-06-01T07:00:00",
         "distance": 10000, "moving_time": 3000, "total_elevation_gain": 42,
         "average_heartrate": 150.4, "max_heartrate": 170, "name": "Run"},
        {"id": 2, "sport_type": "Walk", "start_date_local": "2026-06-02T07:00:00",
         "distance": 3000, "moving_time": 1800, "name": "Walk"},
        {"id": 3, "sport_type": "WeightTraining", "start_date_local": "2026-06-03T07:00:00",
         "distance": 0, "moving_time": 3600, "name": "Lift"},
    ]
    acts = N.build_activities(raw)
    ids = {a["id"] for a in acts}
    assert ids == {"1", "3"}  # Walk filtered out, ids are strings

    run = next(a for a in acts if a["id"] == "1")
    assert run["type"] == "Run"
    assert run["distance_km"] == 10.0
    assert run["pace_min_km"] == 5.0  # 3000s / 10km = 300s/km = 5.0
    assert run["avg_heart_rate_bpm"] == 150  # rounded
    assert "lat" not in run and "start_latlng" not in run  # no location

    lift = next(a for a in acts if a["id"] == "3")
    assert lift["type"] == "Strength"
    assert lift["pace_min_km"] is None


def test_guardrail_status_thresholds():
    from datetime import datetime, timedelta
    ref = datetime(2026, 6, 30)

    def run(days_ago, km):
        d = (ref - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        return {"date": d, "type": "Run", "distance_km": km, "pace_min_km": 5.0}

    # acute (7d) baixo vs crônico => ok
    acts = [run(20, 40), run(14, 40), run(3, 8)]
    g = N.acute_chronic_ratio(acts, ref)
    assert g["metric"] == "acute_chronic_ratio"
    assert g["status"] in {"ok", "warning", "danger"}

    # sem corridas recentes => unknown
    g2 = N.acute_chronic_ratio([], ref)
    assert g2["status"] == "unknown"


def test_quarter_of():
    assert N.quarter_of(1) == 1
    assert N.quarter_of(3) == 1
    assert N.quarter_of(4) == 2
    assert N.quarter_of(12) == 4


def test_acute_effort_load_unknown_with_little_history():
    from datetime import datetime
    ref = datetime(2026, 7, 6)
    acts = [{"date": "2026-07-04", "relative_effort": 93},
            {"date": "2026-07-06", "relative_effort": 10}]
    load = N.acute_effort_load(acts, ref)
    assert load["metric"] == "acute_effort_load"
    assert load["value"] == 103.0
    assert load["status"] == "unknown"  # <14 dias de histórico


def test_acute_effort_load_flags_above_p90():
    from datetime import datetime, timedelta
    ref = datetime(2026, 7, 6)
    acts = []
    # 90 dias de esforço baixo e estável, exceto os últimos 3 dias (pico)
    for i in range(3, 93):
        d = (ref - timedelta(days=i)).strftime("%Y-%m-%d")
        acts.append({"date": d, "relative_effort": 10})
    for i in range(3):
        d = (ref - timedelta(days=i)).strftime("%Y-%m-%d")
        acts.append({"date": d, "relative_effort": 200})

    load = N.acute_effort_load(acts, ref)
    assert load["status"] == "warning"
    assert load["value"] > load["baseline_p90"]
