"""Testes do ingester do Apple Health (etl/merge_health.py).

Testam a função pura parse_hae contra um payload representativo do Health Auto Export,
sem tocar em data/private/ (seguro no CI).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "etl"))

import merge_health as H  # noqa: E402


SAMPLE = {
    "data": {
        "metrics": [
            {"name": "resting_heart_rate", "units": "bpm",
             "data": [{"date": "2026-06-28 07:00:00 -0300", "qty": 52}]},
            {"name": "heart_rate_variability", "units": "ms",
             "data": [{"date": "2026-06-28 03:00:00 -0300", "qty": 44.6}]},
            {"name": "weight_body_mass", "units": "kg",
             "data": [{"date": "2026-06-28 20:01:00 -0300", "qty": 109.35}]},
            {"name": "body_fat_percentage", "units": "%",
             "data": [{"date": "2026-06-28 20:01:00 -0300", "qty": 33.5}]},
            {"name": "sleep_analysis", "units": "hr",
             "data": [{"date": "2026-06-28 06:00:00 -0300",
                       "asleep": 6.8, "deep": 1.1, "rem": 1.6, "core": 4.1,
                       "awake": 0.3, "inBed": 7.4}]},
        ]
    }
}


def test_parse_hae_extracts_scalars_and_sleep():
    out = H.parse_hae(SAMPLE)
    day = out["2026-06-28"]
    assert day["resting_hr"] == 52
    assert day["hrv_ms"] == 44.6
    assert day["weight_kg"] == 109.35
    assert day["body_fat_pct"] == 33.5
    assert day["sleep"]["deep"] == 1.1
    assert day["sleep"]["inBed"] == 7.4


def test_parse_hae_groups_by_day():
    out = H.parse_hae(SAMPLE)
    assert set(out.keys()) == {"2026-06-28"}


def test_parse_hae_handles_empty():
    assert H.parse_hae({}) == {}
    assert H.parse_hae({"data": {"metrics": []}}) == {}
