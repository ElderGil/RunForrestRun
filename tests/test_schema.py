"""Contract tests for the generated JSON files (ADR-003).

Validates the data currently in /data so a broken ETL output never ships.
"""

import json
from pathlib import Path

import pytest

DATA = Path(__file__).parent.parent / "data"

LOCATION_FIELDS = {"lat", "lng", "start_latlng", "end_latlng", "map"}

# Peso corporal na faixa adulta (qualquer valor em kg de 2 ou 3 dígitos), diagnóstico e
# histórico ortopédico. Nomes de campo como `bmi` podem aparecer nas skills (descrevem o
# health.json); valores e diagnósticos não. Sem números reais do atleta aqui: o teste é público.
PERSONAL_PATTERNS = [r"\b\d{2,3}[.,]?\d*\s?kg\b", r"\bobes", r"\blca\b", r"\bmenisco\b"]


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
    assert g["status"] in {"ok", "warning", "danger", "unknown", "rebuilding"}
    assert g["threshold_warning"] < g["threshold_danger"]
    assert {"total_sessions", "focus"} <= d["strength"].keys()

    le = d["load_guardrail"]
    assert le["metric"] == "acute_effort_load"
    assert le["status"] in {"ok", "warning", "unknown"}


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
    assert d["schema_version"] in {"1.0", "2.0", "3.0"}
    assert len(d["days"]) == 7
    valid = {"run", "strength", "rest"}
    for day in d["days"]:
        for item in day["items"]:
            assert item["type"] in valid

    if d["schema_version"] == "3.0":
        # Plano rolante (ADR-005): janela de 7 dias consecutivos a partir de window_start.
        from datetime import date, timedelta

        assert {"window_start", "window_end"} <= d.keys()
        start = date.fromisoformat(d["window_start"])
        assert d["window_end"] == (start + timedelta(days=6)).isoformat()
        for i, day in enumerate(d["days"]):
            assert day["date"] == (start + timedelta(days=i)).isoformat()
            assert day["status"] in {"planned", "done", "missed"}

        # Fase opcional (ADR-006): alimenta o hero da página.
        if "phase" in d:
            assert isinstance(d["phase"]["label"], str) and d["phase"]["label"]
            assert isinstance(d["phase"].get("detail", ""), str)


def test_weekly_plan_has_no_personal_data():
    """O plano é público: nunca pode vazar peso/medidas/idade (ficam em data/private/)."""
    path = DATA / "weekly_plan.json"
    if not path.exists():
        pytest.skip("weekly_plan.json ainda não gerado")
    import re

    blob = path.read_text().lower()
    for pattern in (*PERSONAL_PATTERNS, r"\bbmi\b", r"\bimc\b", "gordura visceral", "cirurgia"):
        assert not re.search(pattern, blob), f"possível vazamento de dado pessoal: {pattern!r}"


PUBLIC_TEXTS = [DATA / "coaches.json", *sorted((DATA.parent / "skills").glob("*/SKILL.md"))]


@pytest.mark.parametrize("path", PUBLIC_TEXTS, ids=lambda p: str(p.relative_to(DATA.parent)))
def test_public_texts_have_no_personal_data(path):
    """Coaches e skills são públicos (ADR-006): perfil, peso e histórico médico só em data/private/."""
    import re

    blob = path.read_text().lower()
    for pattern in PERSONAL_PATTERNS:
        assert not re.search(pattern, blob), f"possível vazamento de dado pessoal em {path.name}: {pattern!r}"
