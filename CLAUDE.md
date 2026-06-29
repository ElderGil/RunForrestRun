# RunForrestRun 🏃

## Contexto do Projeto

**O que é:** Página pública no GitHub Pages que documenta e visualiza a jornada de treinamento do Elder até uma maratona completa.

**Por que existe:** Documentar publicamente uma jornada real de treinamento — com dados, métricas e evolução visíveis — do jeito que um engenheiro documenta um projeto de software.

**Objetivo final:** Correr uma maratona completa até o final de 2027.

**Objetivo intermediário:** Meia maratona em Pomerode — 17/18 de outubro de 2026.

**Perfil do atleta (resumo público):**
- Nível: Intermediário; correndo há mais de 1,5 anos, já completou uma meia maratona.
- Modalidades: Corrida (principal), Musculação/Força (programa A/B/C fixo), Bike (hobby).
- Fontes de dados: Strava (desde jun/2024), Apple Health (sono/recuperação/composição via Amazfit + balança OKOK).
- **Perfil completo, peso e histórico médico:** em `data/private/athlete.json` (privado — nunca commitado, nunca publicado).

---

## Stack Técnica

| Camada | Tecnologia | Motivo |
|---|---|---|
| Fontes de dados | Strava API + Apple Health (sono/recuperação/composição) | Dados reais de treino e saúde |
| ETL | Python, rodado pela **routine diária do Claude** | Simples, gratuito, versionado, sem Secrets |
| Armazenamento público | JSON estático no repo (`data/*.json`) | Sem banco; compatível com GitHub Pages |
| Armazenamento privado | JSON local gitignored (`data/private/`) | Dados pessoais/médicos nunca publicados |
| Página | React + Vite + Recharts | Estático, rápido, sem servidor |
| CI/CD | GitHub Actions (CI de testes/build + deploy do Pages) | Gratuito |
| Agentes/Skills | Claude Skills (running-coach + strength-coach) | Coaches que negociam o plano |
| Metodologia | CLAUDE.md + PRD + ADR + Tests | Engenharia orientada a documentação |

---

## Arquitetura (sumário)

```
Strava API ─────────┐
                    ├──► routine diária do Claude (Python ETL no Mac · 11:08 BRT)
Apple Health ───────┘       merge_strava → normalize → merge_health → coaches negociam
  (Health Auto Export
   → Dropbox/iCloud → Mac)
                            ↓
   data/*.json  (PÚBLICO, sem dado pessoal)   +   data/private/*.json  (LOCAL, gitignored)
                            ↓ git push
            GitHub Actions (pages.yml) → build Vite → GitHub Pages
                            ↓
            App React + Recharts (abas Jornada / Plano)
```

**Princípios:**
- **Sem servidor:** tudo estático, tudo versionado.
- **Dados como código:** os JSONs públicos ficam no repositório.
- **Privacidade:** dados pessoais/médicos só em `data/private/` — gitignored e não copiados pelo build (o Vite só copia `data/*.json` da raiz). Nunca vão à página nem ao repo público.
- **Automação discreta:** a routine do Claude roda diariamente (11:08 BRT), atualiza os dados e publica.
- **Transparência:** código e dados não-pessoais são abertos.

---

## Estrutura de Pastas

```
RunForrestRun/
├── CLAUDE.md                  # Este arquivo (memória do projeto)
├── README.md                  # Apresentação pública + arquitetura
├── docs/
│   ├── PRD.md
│   ├── automation-runbook.md  # Procedimento da routine diária
│   └── adr/
│       ├── 001-etl-architecture.md
│       ├── 002-page-stack.md
│       ├── 003-data-schema.md
│       ├── 004-github-actions.md
│       └── 005-rolling-plan-and-coach-negotiation.md
├── etl/
│   ├── merge_strava.py        # Ingestão incremental do Strava (via routine)
│   ├── merge_health.py        # Ingestão do Apple Health (Health Auto Export)
│   ├── normalize.py           # Normaliza e calcula KPIs + guardrail ACWR
│   └── requirements.txt
├── data/                      # PÚBLICO (vai para a página)
│   ├── activities.json        # Atividades normalizadas (sem localização)
│   ├── activities_raw.json    # Store bruto (intermediário)
│   ├── kpis.json · weekly.json · monthly.json · quarterly.json
│   ├── coaches.json           # Perfis dos coaches
│   ├── weekly_plan.json       # Plano rolante de 7 dias (schema 3.0)
│   └── private/               # LOCAL, gitignored — NUNCA publicado
│       ├── athlete.json           # Perfil, peso, histórico médico
│       ├── body_composition.json  # Bioimpedância OKOK
│       ├── strength_program.json  # Programa A/B/C (base fixa) + análise
│       └── health.json            # Apple Health (sono, FC repouso, VO2máx, peso…)
├── site/                      # App React + Vite + Recharts
│   ├── index.html
│   ├── vite.config.js         # serve /data em dev; copia data/*.json no build
│   └── src/ (App.jsx, components/, data/loaders.js, styles/)
├── skills/
│   ├── running-coach/SKILL.md
│   └── strength-coach/SKILL.md
├── tests/
│   ├── test_etl.py · test_schema.py · test_health_etl.py
└── .github/workflows/
    ├── ci.yml                 # testes + build em cada push/PR
    └── pages.yml              # deploy do Pages quando data/** ou site/** mudam
```

---

## KPIs Monitorados

| KPI | Por que acompanhar |
|---|---|
| Pace médio (min/km) | Performance e evolução de velocidade |
| Distância semanal (km) | Controle de carga — base para periodização |
| Frequência cardíaca média/máx | Eficiência cardiovascular e intensidade |
| Elevação acumulada (m) | Força e resistência muscular |
| Volume mensal (km) | Visão macro da consistência |
| Long run mais longo | Preparação específica para a maratona |
| Consistência (treinos/semana) | Disciplina — o KPI mais importante a longo prazo |
| Guardrail ACWR | Razão carga aguda/crônica — risco de lesão |
| Recuperação (Apple Health) | FC de repouso, sono, VO2máx — quando aliviar/avançar |

---

## Decisões Técnicas (ADRs)

- [x] ADR-001: Arquitetura do ETL (incremental)
- [x] ADR-002: Stack da página (React + Vite + Recharts)
- [x] ADR-003: Schema dos dados normalizados
- [x] ADR-004: Estratégia de atualização (hoje: routine do Claude; GitHub Actions só p/ deploy)
- [x] ADR-005: Plano rolante de 7 dias + negociação dos coaches

---

## Agentes e Skills

Os dois coaches **negociam** o mesmo `data/weekly_plan.json` (plano rolante de 7 dias).
Leem os artifacts privados (`athlete.json`, `strength_program.json`, `health.json`) como
contexto, mas **nunca** escrevem dado pessoal no plano público.

### running-coach
- **Objetivo:** analisar a corrida (Strava + recuperação do Apple Health) e montar os dias de corrida da janela.
- **Outputs:** plano rolante, indicadores, guardrail ACWR, alertas de sobrecarga.

### strength-coach
- **Objetivo:** encaixar o programa A/B/C **fixo** ao redor da corrida, sem trocar exercícios (só reduz série/carga/amplitude ou pausa item, com justificativa).
- **Regras:** perna pesada ≥48h de long run/qualidade; ≥1 descanso na janela; carga dentro do guardrail.

---

## Estado Atual

### Concluído ✅
- [x] PRD, ADR-001..005, CLAUDE.md.
- [x] ETL: ingestão incremental do Strava + normalização (guardrail ACWR).
- [x] Site React + Vite + Recharts (abas Jornada / Plano), light mode.
- [x] Automação diária via **routine do Claude** (sem Secrets) — ver `docs/automation-runbook.md`; allowlist destravado.
- [x] CI (testes + build) e deploy do Pages por push (`pages.yml`).
- [x] Sistema de coach adaptativo (perfis + caixa semanal que reage aos treinos).
- [x] **Plano rolante de 7 dias** (ADR-005, schema 3.0) + coaches negociando o A/B/C fixo.
- [x] **Privacidade:** dados pessoais/médicos em `data/private/` (gitignored) + teste anti-vazamento no plano público.
- [x] **Apple Health:** ingestão de sono/FC repouso/VO2máx/peso via Health Auto Export → Dropbox → `merge_health.py`.
- [x] Testes: ETL, contrato de schema, ingester de health (21 testes, pytest).

### Pendente ⏳
- [ ] HRV (VFC) não chega do Amazfit ao Apple Health — investigar/ativar se possível.
- [ ] Parser do export mensal do OKOK (gordura visceral/água/músculo, que não passam pelo Apple Health).
- [ ] Decidir export automático diário do Health Auto Export (recurso Premium).
- [ ] Guardrail KPI definitivo após análise do histórico real.
- [ ] Monitorar expiração da conexão Strava (alerta proativo).

---

## Convenções

- **Commits:** em inglês, formato `feat:`, `fix:`, `data:`, `docs:`, `chore:`.
- **Branches:** `main` é produção (fluxo de fato: commits diretos na main + deploy automático).
- **Dados:** JSONs com schema versionado — nunca quebrar compatibilidade sem ADR.
- **Privacidade:** nada de dado pessoal/médico fora de `data/private/`.
- **Código Python:** PEP8, docstrings em funções públicas, sem credenciais no código.

---

## Como Rodar Localmente

```bash
# Dependências do ETL (pytest)
pip install -r etl/requirements.txt

# Reprocessar os JSONs a partir do store bruto
python3 etl/normalize.py

# Ingerir Apple Health (se houver export do Health Auto Export; senão é no-op)
python3 etl/merge_health.py

# Servir o site (React + Vite; serve /data automaticamente)
cd site && npm install && npm run dev   # http://localhost:5173

# Testes
python3 -m pytest tests/ -q
```

> A busca do Strava roda na **routine diária do Claude** (sem Secrets) —
> `merge_strava.py` + `normalize.py` + `merge_health.py`. Ver `docs/automation-runbook.md`.

---

## Metodologia

Engenharia orientada a documentação:

1. **PRD primeiro** — define o quê antes do como.
2. **ADR para cada decisão técnica relevante** — registra o raciocínio.
3. **Testes validam contratos de dados** (incl. anti-vazamento de dado pessoal).
4. **CLAUDE.md como memória** — atualizado a cada mudança de estado significativa.

> Regra de ouro: se não está documentado aqui, não é decisão oficial do projeto.
