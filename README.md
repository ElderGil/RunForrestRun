# RunForrestRun 🏃

> Documentando publicamente uma jornada real de treinamento — com dados, métricas e evolução visíveis — do jeito que um engenheiro documenta um projeto de software.

**Objetivo final:** correr uma maratona completa até o final de 2027.
**Objetivo intermediário:** meia maratona em Pomerode — outubro de 2026.

🔗 **Página ao vivo:** https://eldergil.github.io/RunForrestRun/

## Como funciona

```
Strava API → ETL (Python, incremental) → JSON versionado → React/Vite → GitHub Pages
```

Um workflow do GitHub Actions roda diariamente às 11h (BRT), busca **só as
atividades novas** do Strava (incremental), recalcula os KPIs, commita os JSONs
e publica o site. A página é estática e orientada a dados — sem servidor.

## Estrutura

| Pasta | O quê |
|---|---|
| `etl/` | `merge_strava.py` (ingestão incremental) e `normalize.py` (KPIs + guardrail) |
| `data/` | JSONs versionados (`activities`, `weekly`, `quarterly`, `kpis`, `weekly_plan`) |
| `site/` | App React + Vite + Recharts (`src/`) |
| `skills/` | `running-coach` e `strength-coach` (geram o plano semanal) |
| `docs/` | PRD e ADRs (decisões técnicas registradas) |
| `tests/` | Testes de ETL e contrato de schema (pytest) |
| `.github/workflows/` | CI (testes + build) e automação diária |

## Rodar localmente

```bash
# Site (Vite serve /data automaticamente em dev)
cd site && npm install && npm run dev   # http://localhost:5173

# Reprocessar os JSONs a partir do store bruto
python3 etl/normalize.py

# Testes
python3 -m pytest tests/ -q
```

A busca de dados do Strava é feita por uma **routine diária do Claude** (sem
Secrets), que usa a conexão Strava e roda `etl/merge_strava.py` + `etl/normalize.py`.
Ver [`docs/automation-runbook.md`](docs/automation-runbook.md).

## KPIs acompanhados

Pace médio · volume semanal · long run mais longo · consistência · FC média/máx ·
elevação · treinos de força · **guardrail** (razão carga aguda/crônica).

---

Dados reais do [Strava](https://www.strava.com/). Código aberto.
