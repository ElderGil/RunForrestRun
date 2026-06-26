# RunForrestRun 🏃

> Documentando publicamente uma jornada real de treinamento — com dados, métricas e evolução visíveis — do jeito que um engenheiro documenta um projeto de software.

**Objetivo final:** correr uma maratona completa até o final de 2027.
**Objetivo intermediário:** meia maratona em Pomerode — outubro de 2026.

🔗 **Página ao vivo:** https://eldergil.github.io/RunForrestRun/site/

## Como funciona

```
Strava API → ETL (Python) → JSON versionado → GitHub Pages (Chart.js)
```

Um workflow do GitHub Actions roda diariamente à meia-noite (BRT), busca as
atividades do Strava, recalcula os KPIs e commita os JSONs atualizados. A
página é 100% estática — sem servidor, sem banco de dados.

## Estrutura

| Pasta | O quê |
|---|---|
| `etl/` | `strava_fetch.py` (busca) e `normalize.py` (KPIs) |
| `data/` | JSONs normalizados versionados (`activities`, `weekly`, `monthly`, `kpis`) |
| `site/` | Página estática (`index.html`, `style.css`, `charts.js`) |
| `docs/` | PRD e ADRs (decisões técnicas registradas) |
| `.github/workflows/` | Automação diária |

## Rodar localmente

```bash
# Servir a página (a partir da raiz do repo, para o site achar /data)
python3 -m http.server 8000
# abrir http://localhost:8000/site/

# Reprocessar KPIs a partir do dump bruto
python3 etl/normalize.py

# Atualizar dados do Strava (requer credenciais)
export STRAVA_CLIENT_ID=... STRAVA_CLIENT_SECRET=... STRAVA_REFRESH_TOKEN=...
python3 etl/strava_fetch.py && python3 etl/normalize.py
```

## KPIs acompanhados

Pace médio · volume semanal/mensal · long run mais longo · consistência ·
treinos de força · elevação acumulada.

---

Dados reais do [Strava](https://www.strava.com/). Código aberto.
