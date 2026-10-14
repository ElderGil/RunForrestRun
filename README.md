# RunForrestRun

Dois coaches de IA montam meu treino e o ajustam todo dia com base no que eu realmente
fiz, dormi e aguentei:

- **Coach de corrida:** monta as corridas da semana e controla a carga para evitar lesão.
- **Coach de força:** encaixa o programa de musculação ao redor da corrida.

O objetivo é saúde: correr e treinar com constância por muitos anos, sem me machucar no
caminho.

[Página ao vivo](https://eldergil.github.io/RunForrestRun/) · [Como funciona](#como-funciona) · [Decisões de arquitetura](docs/adr/)

## O que ele faz

Apps de treino entregam uma planilha pronta e esperam que a vida se encaixe nela. Aqui é
o contrário: o plano se ajusta ao que de fato aconteceu.

- **Plano que acompanha a vida real.** Todo dia o sistema lê o que foi corrido, levantado
  e dormido, e refaz os próximos 7 dias. Se você passou semanas sem correr, o plano
  recomeça de onde o corpo está, não de onde a planilha parou.
- **Dois coaches que negociam.** O coach de corrida e o de força dividem a mesma semana.
  A corrida define o esqueleto e a força encaixa o programa A/B/C ao redor, sem trocar
  exercícios. Cada ajuste fica registrado com o motivo.
- **Freio contra lesão.** Dois guardrails vigiam a carga: a razão aguda/crônica da corrida
  e o esforço somado de corrida, força e bike, comparado ao próprio histórico do atleta.
  O descanso sai desses números, não de um dia fixo no calendário.
- **Custo zero, sem servidor.** Os dados ficam em JSON versionado, o site é estático no
  GitHub Pages e a atualização é feita por uma routine diária do Claude. Não há banco,
  API própria nem segredo guardado no repositório.
- **Aberto, mas não exposto.** O código e as métricas de treino são públicos. Peso, saúde e
  histórico médico ficam só na máquina local, e um teste quebra o build se algo vazar.

## Momento atual

Desde junho de 2024 são mais de 1.000 km corridos e 250 treinos registrados. Depois de
algumas semanas longe da corrida, mantendo só a força, estou voltando a correr. A volta é
gradual ([protocolo de volta à corrida](docs/adr/006-health-goal-and-return-to-running.md)),
com a força sustentando a constância enquanto a base de corrida se reconstrói.

## Feito como software

O projeto segue o processo de um produto: [PRD](docs/PRD.md) antes do código,
[ADRs](docs/adr/) para cada decisão técnica, testes de contrato sobre os dados e CI em
cada push. O histórico de commits funciona também como diário de treino.

---

## Como funciona

```
Strava ───────────┐
                  ├──► routine diária do Claude (Python, no Mac · 11:08 BRT)
Apple Health ─────┘        merge_strava → normalize → merge_health → coaches negociam
  (export → nuvem → Mac)
                           │
        ┌──────────────────┴───────────────────┐
   data/*.json  (PÚBLICO)              data/private/*.json  (LOCAL, gitignored)
   atividades, KPIs, plano             perfil, peso, saúde, programa de força
                           │ git push
              GitHub Actions → build Vite → GitHub Pages
                           │
              App React + Recharts (Jornada / Plano)
```

- **Sem servidor.** Tudo é arquivo estático versionado. A página é React puro servido pelo GitHub Pages.
- **Atualização diária.** Uma routine do Claude busca só as atividades novas do Strava, lê o Apple Health, recalcula os KPIs, deixa os coaches renegociarem o plano e publica. Sem Secrets e sem cron de servidor.
- **Plano rolante.** `running-coach` e `strength-coach` negociam um único plano de 7 dias (hoje + 6), respeitando a recuperação e o guardrail de carga.

## Privacidade: o que não é exposto

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
elevação · treinos de força · **guardrails** (razão carga aguda/crônica da corrida e esforço
agudo de corrida+força+bike) · recuperação (sono, FC de repouso, VO2máx).

---

Dados reais do [Strava](https://www.strava.com/) e do Apple Health. Código aberto; dados pessoais, não.
