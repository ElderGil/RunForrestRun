"""Ingestão dos dados de recuperação do Apple Health (iOS).

Por quê assim: o Apple Health **não tem API no macOS** e os dados vivem no iPhone.
Como a routine diária roda no Mac, ela **lê um arquivo local** sincronizado pelo
iCloud Drive — sem servidor, no mesmo espírito do resto do projeto.
Ver docs/automation-runbook.md.

Suporta DOIS formatos de export, detectados automaticamente pelo shape do JSON:
1. **Health Auto Export** (app, requer assinatura Premium para automação agendada)
   — `{"data": {"metrics": [...]}}`, ver `parse_hae`.
2. **Atalho (Shortcuts) caseiro, gratuito** — dicionário simples e plano montado
   por uma automação nativa do app Atalhos da Apple (sem terceiros, sem custo),
   lendo o HealthKit direto via ações `Get Health Sample`/`Find Health Samples`.
   Ver `parse_shortcuts_export` e o guia de montagem no chat/README.

Uso:
    python etl/merge_health.py [export.json]

Sem argumento, usa o JSON mais recente sob a pasta do export no iCloud (mesmos
nomes de arquivo servem para os dois formatos — ver HAE_GLOBS).
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


# Campos escalares aceitos de um export do Atalho caseiro — mesmos nomes de saída
# que o Health Auto Export já usa, pra não duplicar schema em health.json.
SHORTCUT_SCALAR_FIELDS = set(SIMPLE.values())


def parse_shortcuts_export(payload: dict) -> dict:
    """JSON de uma automação caseira no app Atalhos (Shortcuts) -> mesmo shape do
    parse_hae: { 'YYYY-MM-DD': {campos...} }.

    Shape esperado (um dicionário só, achatado — fácil de montar com uma única
    ação "Dicionário" no Atalhos, sem precisar replicar o array de métricas
    aninhado do Health Auto Export):

        {"date": "2026-07-07", "resting_hr": 47, "vo2_max": 46,
         "sleep": {"totalSleep": 7.2, "deep": 1.5, "rem": 1.6, "core": 4.1,
                   "awake": 0.3, "inBed": 7.5}}

    Aceita tanto um único dia (dict) quanto uma lista de dias (uma automação que
    rode 1x/dia normalmente só manda o dia atual — merge_into já sabe mesclar).
    """
    days = payload if isinstance(payload, list) else [payload]
    out: dict[str, dict] = {}
    for day in days:
        d = _day(day.get("date")) if len(str(day.get("date", ""))) > 10 else day.get("date")
        if not d:
            continue
        rec = {k: round(float(day[k]), 2) for k in SHORTCUT_SCALAR_FIELDS if day.get(k) is not None}
        if day.get("sleep"):
            sleep = {k: round(float(v), 2) for k, v in day["sleep"].items()
                      if k in SLEEP_FIELDS and v is not None}
            if sleep:
                rec["sleep"] = sleep
        if rec:
            out[d] = rec
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
        "source": "Apple Health (Health Auto Export ou Atalho caseiro)",
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
        print("Health: nenhum export encontrado (Health Auto Export ou Atalho) — no-op.")
        return 0
    raw = json.loads(src.read_text())
    is_hae = isinstance(raw, dict) and "metrics" in (raw.get("data") or {})
    records = parse_hae(raw) if is_hae else parse_shortcuts_export(raw)
    before, after = merge_into(OUT, records)
    fmt = "Health Auto Export" if is_hae else "Atalho caseiro"
    print(f"Health ({fmt}): {src.name} -> {len(records)} dia(s); store {before} -> {after}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
