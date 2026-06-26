# ADR-001 — Arquitetura do ETL

**Data:** 2026-06-25  
**Status:** Aceito  
**Autores:** Elder Gil  

---

## Contexto

A página RunForrestRun é estática (GitHub Pages) e não pode executar código server-side em tempo real. Os dados de treino vivem na Strava API e precisam ser buscados, normalizados e disponibilizados como arquivos estáticos que a página possa consumir via JavaScript.

A decisão define como esse pipeline funciona: quem busca os dados, quando, onde armazena e como a página os acessa.

Requisitos que guiam a decisão:
- Sem servidor próprio (custo zero, manutenção zero)
- Credenciais da Strava nunca expostas publicamente
- Dados atualizados diariamente de forma automática
- JSONs versionados no repositório (dados como código)
- Histórico disponível desde junho de 2024

---

## Opções Consideradas

### Opção A — Python + GitHub Actions (cron diário) ✅ Escolhida

Script Python roda via GitHub Actions todos os dias. Busca dados da Strava API usando credenciais armazenadas em GitHub Secrets, gera JSONs normalizados e faz commit automático no repositório. A página lê os JSONs diretamente.

**Prós:**
- Credenciais protegidas em GitHub Secrets — nunca no código
- Dados versionados no repositório (histórico auditável)
- Página carrega instantaneamente (sem chamada de API em runtime)
- Totalmente gratuito (GitHub Actions free tier)
- Simples de debugar: logs do Actions mostram exatamente o que rodou
- Compatível com a integração Strava já existente no Cowork

**Contras:**
- Dados atualizados com até 24h de delay (aceitável para o contexto)
- Requer configuração inicial do workflow e dos Secrets

---

### Opção B — Client-side fetch (JavaScript no browser)

A página faz chamadas diretas à Strava API via JavaScript no browser do visitante.

**Prós:**
- Dados sempre em tempo real
- Sem pipeline de ETL para manter

**Contras:** ❌ Descartada
- Expõe credenciais da Strava no código público (inaceitável)
- CORS bloquearia as chamadas diretas sem proxy
- Dependência de conexão do visitante para renderizar dados

---

### Opção C — Serviço externo (Pipedream, Zapier, etc.)

Serviço de terceiro faz a ponte entre Strava e o repositório.

**Prós:**
- Configuração sem código

**Contras:** ❌ Descartada
- Dependência de terceiro (pode sair do ar, mudar de preço)
- Menos controle sobre o schema dos dados
- Adiciona complexidade desnecessária para o que o GitHub Actions já resolve

---

## Decisão

**Opção A: Python + GitHub Actions.**

Pipeline ETL em Python rodando diariamente via cron no GitHub Actions. Credenciais da Strava armazenadas em GitHub Secrets. JSONs gerados e versionados em `/data/` no repositório.

---

## Estratégia de Busca — Incremental

**Decisão:** a busca é **incremental**, não um full-fetch diário.

O arquivo `data/activities_raw.json`, versionado no Git, é o **store de
registro** (onde os dados já baixados ficam). A cada run, o `strava_fetch.py`:

1. Lê o store existente e descobre o `start_date` mais recente já armazenado
2. Busca na Strava apenas atividades posteriores a esse timestamp, com uma
   janela de sobreposição de 2 dias (`after = último - 48h`) para capturar
   atividades editadas após o registro
3. Faz merge no store deduplicando por `id` (a versão recém-baixada vence,
   refletindo edições)
4. Em um checkout limpo sem store, faz **backfill** desde junho de 2024

**Rationale:** respeita o rate limit da Strava (100 req/15min, 1000/dia),
torna o run diário barato e mantém a coerência com o princípio "dados como
código" — o repositório é o banco de dados. Os campos de localização são
removidos antes de gravar no store (ADR-003, regra 5).

O `normalize.py` consome o store e regera os JSONs agregados a cada run
(agregação é determinística e barata; não há estado incremental nela).

---

## Fluxo do Pipeline

```
GitHub Actions (cron: 11h Brasília — ver ADR-004)
    ↓
strava_fetch.py
    → Autentica via OAuth com token em GitHub Secrets
    → Lê data/activities_raw.json (store versionado)
    → Busca incremental: só atividades após o último timestamp (+overlap 48h)
    → Remove campos de localização
    → Merge dedup por id → grava o store atualizado
    ↓
normalize.py
    → Mantém só Run / WeightTraining / Ride
    → Calcula KPIs por atividade (pace decimal, sem localização)
    → Agrega por semana (12 meses) e quarter (desde jun/2024)
    → Calcula o guardrail KPI (razão carga aguda/crônica)
    → Aplica schema versionado (ver ADR-003)
    ↓
Commit automático em /data/
    → activities_raw.json   (store bruto)
    → activities.json       (normalizado — base dos coaches)
    → kpis.json
    → weekly.json
    → quarterly.json
    ↓
GitHub Pages serve os JSONs
    ↓
site React lê e renderiza os dados
```

---

## Consequências

**O que essa decisão facilita:**
- ETL completamente auditável — cada run do Actions fica logado
- Dados históricos preservados no Git — possível reverter qualquer estado
- Zero custo de infraestrutura
- Fácil de evoluir: adicionar novos KPIs é só mudar o `normalize.py` e rodar o pipeline

**O que essa decisão limita:**
- Dados não são real-time (delay de até 24h)
- Requer rerun manual do Actions se a Strava API falhar em um dia

**Dívida técnica gerada:**
- Implementar retry logic no script para falhas transitórias da API
- Monitorar expiração do refresh token do Strava (tokens OAuth expiram)

---

## Referências

- [Strava API Documentation](https://developers.strava.com/docs/)
- [GitHub Actions — scheduled workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
- ADR-003 — Schema dos dados normalizados (define o contrato dos JSONs gerados aqui)
