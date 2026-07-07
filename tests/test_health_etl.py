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
            {"name": "vo2_max", "units": "mL/min·kg",
             "data": [{"date": "2026-06-28 09:00:00 -0300", "qty": 45.2}]},
            {"name": "lean_body_mass", "units": "kg",
             "data": [{"date": "2026-06-28 20:01:00 -0300", "qty": 72.6}]},
            # Estrutura real: 'asleep' pode vir 0; o tempo dormido é 'totalSleep'.
            {"name": "sleep_analysis", "units": "hr",
             "data": [{"date": "2026-06-28 06:00:00 -0300",
                       "asleep": 0.0, "deep": 1.1, "rem": 1.6, "core": 4.1,
                       "awake": 0.3, "inBed": 7.4, "totalSleep": 6.8}]},
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
    assert day["vo2_max"] == 45.2
    assert day["lean_mass_kg"] == 72.6
    assert day["sleep"]["deep"] == 1.1
    assert day["sleep"]["totalSleep"] == 6.8


def test_parse_hae_groups_by_day():
    out = H.parse_hae(SAMPLE)
    assert set(out.keys()) == {"2026-06-28"}


def test_parse_hae_handles_empty():
    assert H.parse_hae({}) == {}
    assert H.parse_hae({"data": {"metrics": []}}) == {}


SHORTCUT_SAMPLE = {
    "date": "2026-07-07",
    "resting_hr": 47,
    "respiratory_rate": 14.8,
    "vo2_max": 46,
    "hrv_ms": 42.1,
    "sleep": {"totalSleep": 7.2, "core": 4.1, "deep": 1.5, "rem": 1.6,
              "awake": 0.3, "inBed": 7.5},
}


def test_parse_shortcuts_export_single_day():
    out = H.parse_shortcuts_export(SHORTCUT_SAMPLE)
    day = out["2026-07-07"]
    assert day["resting_hr"] == 47
    assert day["vo2_max"] == 46
    assert day["hrv_ms"] == 42.1
    assert day["sleep"]["totalSleep"] == 7.2


def test_parse_shortcuts_export_accepts_list_of_days():
    out = H.parse_shortcuts_export([SHORTCUT_SAMPLE, {**SHORTCUT_SAMPLE, "date": "2026-07-08", "resting_hr": 45}])
    assert set(out.keys()) == {"2026-07-07", "2026-07-08"}
    assert out["2026-07-08"]["resting_hr"] == 45


def test_parse_shortcuts_export_handles_empty():
    assert H.parse_shortcuts_export({}) == {}
    assert H.parse_shortcuts_export({"date": "2026-07-07"}) == {}
