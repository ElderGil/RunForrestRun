# RunForrestRun 🏃

## Contexto do Projeto

**O que é:** Página pública no GitHub Pages que documenta e visualiza a jornada de treinamento do Elder até uma maratona completa.

**Por que existe:** Documentar publicamente uma jornada real de treinamento — com dados, métricas e evolução visíveis — do jeito que um engenheiro documenta um projeto de software.

**Objetivo final:** Correr uma maratona completa até o final de 2027.

**Objetivo intermediário:** Meia maratona em Pomerode — 17/18 de outubro de 2026.

**Perfil do atleta:**
- Nível: Intermediário
- Histórico: Correndo há mais de 1,5 anos, já completou uma meia maratona
- Modalidades: Corrida (principal), Musculação/Força (foco em pernas, inclui superiores), Bike (hobby)
- Dados disponíveis: histórico Strava desde junho de 2024 (2 anos)

---

## Stack Técnica

| Camada | Tecnologia | Motivo |
|---|---|---|
| Fonte de dados | Strava API | Dados reais de treino |
| ETL | Python + GitHub Actions | Simples, gratuito, versionado |
| Armazenamento | JSON estático no repo | Sem banco de dados, compatível com GitHub Pages |
| Página | HTML + JS + Chart.js | Estático, rápido, sem servidor |
| Versionamento | Git + GitHub | CI/CD gratuito |
| Agentes/Skills | Claude Cowork Skills | Coach de corrida e força |
| Metodologia | CLAUDE.md + PRD + ADR + Tests | Engenharia orientada a documentação |

---

## Arquitetura (sumário)

```
Strava API
    ↓ (GitHub Actions — cron diário)
ETL Python
    ↓
JSON normalizado (/data/*.json)
    ↓
GitHub Pages (index.html)
    ↓
Visualização com Chart.js
```

**Princípios:**
- Sem servidor: tudo estático, tudo versionado
- Dados como código: os JSONs gerados ficam no repositório
- Automação discreta: GitHub Actions roda à meia-noite e atualiza os dados
- Transparência total: qualquer pessoa pode ver os dados e o código

---

## Estrutura de Pastas (planejada)

```
RunForrestRun/
├── CLAUDE.md                  # Este arquivo
├── README.md                  # Apresentação pública do projeto
├── docs/
│   ├── PRD.md                 # Product Requirements Document
│   └── adr/
│       ├── 001-etl-architecture.md
│       ├── 002-page-stack.md
│       └── 003-data-schema.md
├── etl/
│   ├── merge_strava.py        # Ingestão incremental do Strava (via routine)
│   ├── normalize.py           # Normaliza e calcula KPIs
│   └── requirements.txt
├── data/
│   ├── activities.json        # Histórico de atividades
│   ├── kpis.json              # KPIs calculados
│   └── weekly.json            # Resumo semanal
├── site/
│   ├── index.html             # Página principal
│   ├── style.css
│   └── charts.js
├── skills/
│   ├── running-coach/
│   │   └── SKILL.md
│   └── strength-coach/
│       └── SKILL.md
├── tests/
│   ├── test_etl.py
│   └── test_schema.py
└── .github/
    └── workflows/
        └── daily-update.yml   # Atualização automática diária
```

---

## KPIs Monitorados

| KPI | Por que acompanhar |
|---|---|
| Pace médio (min/km) | Indicador direto de performance e evolução de velocidade |
| Distância semanal (km) | Controle de carga de treino — base para periodização |
| Frequência cardíaca média | Eficiência cardiovascular — quanto esforço para o mesmo pace |
| FC máxima | Intensidade real dos treinos |
| Elevação acumulada (m) | Força e resistência muscular |
| Tempo em zona de FC | Distribuição de intensidade — polarização do treino |
| Volume mensal (km) | Visão macro da consistência |
| Long run mais longo | Preparação específica para maratona |
| Consistência (treinos/semana) | Disciplina — o KPI mais importante a longo prazo |
| TSS (Training Stress Score) | Carga total de estresse do treino (se disponível via Strava) |

---

## Decisões Técnicas (ADRs)

- [ ] ADR-001: Arquitetura do ETL
- [ ] ADR-002: Stack da página (HTML estático vs framework)
- [ ] ADR-003: Schema dos dados normalizados
- [ ] ADR-004: Estratégia de atualização (GitHub Actions)

---

## Agentes e Skills

### running-coach
- **Objetivo:** Analisar treinos de corrida e sugerir sessões futuras com base nos dados do Strava
- **Inputs:** dados de atividades recentes, KPIs atuais, objetivo (maratona/meia)
- **Outputs:** plano de treino semanal, análise de evolução, alertas de sobrecarga
- **Exibição:** plano de treino semanal gerado é exibido na página pública

### strength-coach
- **Objetivo:** Analisar treinos de força e sugerir sessões complementares ao treino de corrida
- **Inputs:** atividades de musculação registradas, fase do ciclo de treinamento
- **Outputs:** sugestões de treino de força, equilíbrio entre volume e recuperação
- **Exibição:** plano de força gerado é exibido na página pública, integrado ao calendário semanal

---

## Estado Atual

### Concluído ✅
- [x] Repositório criado no GitHub
- [x] Integração Strava conectada no Cowork
- [x] Integração GitHub conectada no Cowork
- [x] CLAUDE.md criado
- [x] PRD — escopo formal da página e dos dados
- [x] ADR-001..004 (ETL incremental, stack React, schema, GitHub Actions)
- [x] ETL: busca incremental + normalização (schema ADR-003, guardrail ACWR)
- [x] Site: React + Vite + Recharts, light mode, abas Jornada/Plano Semanal
- [x] Skills: running-coach e strength-coach + `weekly_plan.json`
- [x] GitHub Actions: CI (testes+build) e deploy diário via Pages Actions
- [x] Testes: ETL e contrato de schema (15 testes, pytest)

- [x] Pages configurado como "GitHub Actions"; site React no ar
- [x] Sistema de coach adaptativo (perfis + caixa semanal que reage aos treinos)
- [x] Automação diária via **routine do Claude** (busca Strava sem Secrets) — ver `docs/automation-runbook.md`

### Pendente ⏳
- [ ] Pré-aprovar as ferramentas da routine ("Run now" 1x) para não pausar em permissões
- [ ] Jornada: trazer últimas atividades no resumo + histórico mensal (2026) / trimestral (2024-25)
- [ ] Guardrail KPI definitivo após análise do histórico real pelo running-coach
- [ ] Monitorar expiração da conexão Strava (alerta proativo)

---

## Convenções

- **Commits:** em inglês, formato `feat:`, `fix:`, `data:`, `docs:`, `chore:`
- **Branches:** `main` é produção; trabalho em `feat/nome-da-feature`
- **PRs:** toda mudança relevante passa por PR com descrição do que foi feito
- **Dados:** JSONs sempre com schema versionado — nunca quebrar compatibilidade sem ADR
- **Código Python:** PEP8, docstrings em funções públicas, sem credenciais no código

---

## Como Rodar Localmente

```bash
# Instalar dependências do ETL (pytest)
cd etl && pip install -r requirements.txt && cd ..

# Reprocessar os JSONs a partir do store bruto
python etl/normalize.py

# Servir o site localmente (React + Vite; serve /data automaticamente)
cd site && npm install && npm run dev   # http://localhost:5173

# Rodar os testes
cd .. && python -m pytest tests/ -q
```

> A busca do Strava roda na **routine diária do Claude** (sem Secrets) —
> `merge_strava.py` + `normalize.py`. Ver `docs/automation-runbook.md`.

---

## Metodologia

Este projeto segue uma metodologia de engenharia orientada a documentação:

1. **PRD primeiro** — define o quê antes do como
2. **ADR para cada decisão técnica relevante** — registra o raciocínio, não só a escolha
3. **Testes antes do código de produção** — valida contratos de dados
4. **Reviewer agent** — revisa PRs antes do merge
5. **CLAUDE.md como memória** — atualizado a cada mudança de estado significativa

> Regra de ouro: se não está documentado aqui, não é decisão oficial do projeto.
