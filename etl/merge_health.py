"""Ingestão dos dados do Apple Health exportados pelo app 'Health Auto Export' (iOS).

Por quê assim: o Apple Health **não tem API no macOS** e os dados vivem no iPhone.
O app Health Auto Export (configurado pelo atleta) exporta um JSON para o iCloud Drive
numa agenda; como a routine diária roda no Mac, ela **lê esse arquivo localmente** —
sem servidor, no mesmo espírito do resto do projeto. Ver docs/automation-runbook.md.

Uso:
    python etl/merge_health.py [export.json]

Sem argumento, usa o JSON mais recente sob a pasta do Health Auto Export no iCloud.
Saída: data/private/health.json (gitignored — dado pessoal), com um registro por dia.
Se não houver export nenhum, faz no-op (não quebra a routine).
"""

from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

PRIVATE = Path(__file__).parent.parent / "data" / "private"
OUT = PRIVATE / "health.json"

# Onde o app Health Auto Export pode depositar o JSON (sincronizado pro Mac).
# Cobrimos iCloud Drive e os mounts de nuvem de terceiros (Google Drive, Dropbox,
# OneDrive vivem sob ~/Library/CloudStorage). A descoberta pega o arquivo mais novo.
CLOUD_ROOTS = [
    Path.home() / "Library/Mobile Documents/com~apple~CloudDocs",  # iCloud Drive
    Path.home() / "Library/CloudStorage",                          # Google Drive / Dropbox / OneDrive
]
HAE_GLOBS = [
    "**/HealthAutoExport*.json",       # nome padrão dos arquivos do app
    "**/HealthAutoExport/**/*.json",   # ou dentro de uma pasta HealthAutoExport
    "**/Health Auto Export/**/*.json",
    "**/HealthMetrics*.json",
]

# Métrica do Health Auto Export -> campo normalizado (valores escalares com `qty`).
SIMPLE = {
    # recuperação
    "heart_rate_variability": "hrv_ms",       # pode não vir (depende do relógio)
    "resting_heart_rate": "resting_hr",
    "respiratory_rate": "respiratory_rate",
    # fitness
    "vo2_max": "vo2_max",
    # composição corporal (da balança, via Apple Health)
    "weight_body_mass": "weight_kg",
    "body_fat_percentage": "body_fat_pct",
    "lean_body_mass": "lean_mass_kg",
    "body_mass_index": "bmi",
    # atividade diária (complementa o Strava: NEAT p/ a meta de perda de gordura)
    "step_count": "steps",
    "active_energy": "active_energy_kcal",
}
SLEEP_FIELDS = ("asleep", "inBed", "core", "deep", "rem", "awake", "totalSleep")


def _day(s: str) -> str:
    """'2026-06-28 07:30:00 -0300' -> '2026-06-28'."""
    return (s or "")[:10]


def parse_hae(payload: dict) -> dict:
    """JSON do Health Auto Export -> { 'YYYY-MM-DD': {campos...} }. Função pura."""
    metrics = (payload.get("data") or {}).get("metrics") or []
    out: dict[str, dict] = {}
    for m in metrics:
        name = (m.get("name") or "").lower()
        points = m.get("data") or []
        if name in SIMPLE:
            field = SIMPLE[name]
            for p in points:
                d = _day(p.get("date"))
                if d and p.get("qty") is not None:
                    out.setdefault(d, {})[field] = round(float(p["qty"]), 2)
        elif name == "sleep_analysis":
            for p in points:
                d = _day(p.get("date"))
                if not d:
                    continue
                sleep = {k: round(float(p[k]), 2) for k in SLEEP_FIELDS if p.get(k) is not None}
                if sleep:
                    out.setdefault(d, {})["sleep"] = sleep
    return out


def merge_into(out_path: Path, records: dict) -> tuple[int, int]:
    """Mescla os registros no health.json (dedup por dia, novo vence)."""
    store = {}
    if out_path.exists():
        store = json.loads(out_path.read_text()).get("days", {})
    before = len(store)
    for d, rec in records.items():
        store.setdefault(d, {}).update(rec)
        store[d]["date"] = d
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "private": True,
        "_warning": "NÃO versionar / NÃO publicar.",
        "source": "Apple Health via Health Auto Export",
        "days": dict(sorted(store.items())),
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return before, len(store)


def _discover() -> Path | None:
    """Acha o export mais recente do Health Auto Export em qualquer nuvem montada."""
    candidates: list[str] = []
    for root in CLOUD_ROOTS:
        if not root.exists():
            continue
        for pat in HAE_GLOBS:
            candidates.extend(glob.glob(str(root / pat), recursive=True))
    if not candidates:
        return None
    return Path(max(set(candidates), key=os.path.getmtime))


def main(argv: list[str]) -> int:
    src = Path(argv[0]) if argv else _discover()
    if not src or not src.exists():
        print("Health: nenhum export do Health Auto Export encontrado — no-op.")
        return 0
    records = parse_hae(json.loads(src.read_text()))
    before, after = merge_into(OUT, records)
    print(f"Health: {src.name} -> {len(records)} dia(s); store {before} -> {after}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
