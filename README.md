# RunForrestRun 🏃

> Documentando publicamente uma jornada real de treinamento — com dados, métricas e evolução visíveis — do jeito que um engenheiro documenta um projeto de software.

**Objetivo final:** correr uma maratona completa até o final de 2027.
**Objetivo intermediário:** meia maratona em Pomerode — outubro de 2026.

🔗 **Página ao vivo:** https://eldergil.github.io/RunForrestRun/

---

## Como funciona

```
Strava ───────────┐
                  ├──► routine diária do Claude (Python, no Mac · 11:08 BRT)
Apple Health ─────┘        merge_strava → normalize → merge_health → coaches negociam
  (Health Auto Export → Dropbox/iCloud → Mac)
                           │
        ┌──────────────────┴───────────────────┐
   data/*.json  (PÚBLICO)              data/private/*.json  (LOCAL, gitignored)
   atividades, KPIs, plano             perfil, peso, saúde, programa de força
                           │ git push
              GitHub Actions → build Vite → GitHub Pages
                           │
              App React + Recharts (Jornada / Plano)
```

- **Sem servidor.** Tudo é arquivo estático versionado; a página é React puro servido pelo GitHub Pages.
- **Atualização diária.** Uma *routine* do Claude busca só as atividades novas do Strava (incremental), lê o Apple Health, recalcula os KPIs, deixa os coaches re-negociarem o plano e publica. Sem Secrets, sem cron de servidor.
- **Coaches que conversam.** `running-coach` e `strength-coach` negociam um único **plano rolante de 7 dias** (hoje + 6): a corrida define o esqueleto, a força encaixa o programa A/B/C ao redor, respeitando recuperação e o guardrail de carga.

## Privacidade — o que NÃO é exposto

O repositório e a página são públicos, então há uma fronteira rígida:

| Público (`data/*.json` → página) | Privado (`data/private/` → só no Mac) |
|---|---|
| Atividades **sem localização**, KPIs, evolução | Perfil, **peso**, idade, histórico médico |
| Plano de treino e notas dos coaches | Bioimpedância (gordura, visceral, água, músculo) |
| Guardrail, recuperação **qualitativa** | Apple Health bruto (sono, FC repouso, VO2máx) |

Garantido por três mecanismos: **(1)** `.gitignore` bloqueia `data/private/`; **(2)** o build do Vite só copia `data/*.json` da raiz (não entra em subpastas), então `private/` nunca vai ao `dist`; **(3)** um **teste de contrato** falha se o plano público contiver peso/IMC/medidas/histórico médico.

## Estrutura

| Pasta | O quê |
|---|---|
| `etl/` | `merge_strava.py` (Strava), `merge_health.py` (Apple Health), `normalize.py` (KPIs + guardrail) |
| `data/` | JSONs públicos (`activities`, `weekly`, `monthly`, `quarterly`, `kpis`, `coaches`, `weekly_plan`) |
| `data/private/` | Dados pessoais (gitignored, nunca publicados) |
| `site/` | App React + Vite + Recharts (`src/`) |
| `skills/` | `running-coach` e `strength-coach` (negociam o plano rolante) |
| `docs/` | PRD, runbook da automação e ADRs (decisões registradas) |
| `tests/` | ETL, contrato de schema e ingester de health (pytest) |
| `.github/workflows/` | CI (testes + build) e deploy do Pages |

## Rodar localmente

```bash
# Site (Vite serve /data automaticamente em dev)
cd site && npm install && npm run dev   # http://localhost:5173

# Reprocessar os JSONs a partir do store bruto
python3 etl/normalize.py

# Testes
python3 -m pytest tests/ -q
```

A busca do Strava e a ingestão do Apple Health rodam na **routine diária do Claude** (sem Secrets), que executa `etl/merge_strava.py` + `etl/normalize.py` + `etl/merge_health.py`. Ver [`docs/automation-runbook.md`](docs/automation-runbook.md).

## KPIs acompanhados

Pace médio · volume semanal/mensal · long run mais longo · consistência · FC média/máx ·
elevação · treinos de força · **guardrail** (razão carga aguda/crônica) · recuperação (sono, FC de repouso, VO2máx).

---

Dados reais do [Strava](https://www.strava.com/) e do Apple Health. Código aberto; dados pessoais, não.
