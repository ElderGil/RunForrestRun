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

## Fluxo do Pipeline

```
GitHub Actions (cron: meia-noite UTC)
    ↓
strava_fetch.py
    → Autentica via OAuth com token em GitHub Secrets
    → Busca atividades desde junho de 2024
    → Filtra por tipo: Run, WeightTraining, Ride
    ↓
normalize.py
    → Calcula KPIs por atividade
    → Agrega por semana, mês e quarter
    → Aplica schema versionado (ver ADR-003)
    ↓
Commit automático em /data/
    → activities.json
    → kpis.json
    → weekly.json
    → quarterly.json
    ↓
GitHub Pages serve os JSONs
    ↓
index.html lê e renderiza os dados
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
