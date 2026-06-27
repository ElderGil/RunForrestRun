# ADR-003 — Schema dos Dados Normalizados

**Data:** 2026-06-25  
**Status:** Aceito  
**Autores:** Elder Gil  

---

## Contexto

O ETL (ADR-001) precisa gerar arquivos JSON que a página React (ADR-002) consome. O schema define o contrato entre essas duas camadas — qualquer mudança não retrocompatível exige um novo ADR.

Requisitos:
- Performance mobile-first: a página não deve carregar mais dados do que precisa
- Separação clara entre dados brutos (para os coaches) e dados agregados (para a página)
- Schema versionado: mudanças não quebram silenciosamente a página
- Sem localização geográfica dos treinos

---

## Opções Consideradas

### Opção A — Um arquivo único (`data.json`)
Tudo em um JSON: atividades, KPIs, semanas, quarters. Descartada — arquivo cresce com o histórico, página carrega tudo mesmo usando só uma parte, ruim para mobile.

### Opção B — Arquivos especializados por uso ✅ Escolhida
Cada arquivo serve uma seção específica da página. ETL calcula e agrega antes de salvar. Página só faz fetch do que precisa.

### Opção C — Atividades brutas + cálculo no browser
ETL gera dados crus, página calcula KPIs em JS. Transfere processamento para o dispositivo do visitante. Ruim para mobile e acopla lógica de KPI ao frontend.

---

## Decisão

**Opção B: arquivos JSON especializados por uso, com schema versionado.**

---

## Schema dos Arquivos

### `data/kpis.json`
KPIs do mês atual. Carregado pelo Hero e pelas seções de Corrida e Força.

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-06-25T00:00:00Z",
  "period": {
    "month": 6,
    "year": 2026,
    "label": "Junho 2026"
  },
  "running": {
    "total_distance_km": 87.4,
    "total_sessions": 12,
    "avg_pace_min_km": 5.42,
    "avg_heart_rate_bpm": 148,
    "max_heart_rate_bpm": 172,
    "total_elevation_m": 310,
    "longest_run_km": 18.2,
    "sessions_per_week": 3.0,
    "guardrail": {
      "metric": "acute_chronic_ratio",
      "value": 1.12,
      "status": "ok",
      "threshold_warning": 1.3,
      "threshold_danger": 1.5,
      "label": "Razão carga aguda/crônica",
      "description": "Compara o volume recente com a média histórica. Acima de 1.3 aumenta risco de lesão."
    }
  },
  "strength": {
    "total_sessions": 8,
    "sessions_per_week": 2.0,
    "focus": "lower_body"
  }
}
```

---

### `data/weekly.json`
Agregações semanais dos últimos 12 meses. Usado pelo gráfico de evolução.

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-06-25T00:00:00Z",
  "weeks": [
    {
      "week_start": "2026-06-16",
      "week_label": "16 Jun",
      "running": {
        "distance_km": 32.1,
        "avg_pace_min_km": 5.38,
        "sessions": 3,
        "avg_heart_rate_bpm": 145
      },
      "strength": {
        "sessions": 2
      }
    }
  ]
}
```

---

### `data/monthly.json`
Agregação mensal do **ano corrente**. Usado pelos cards mensais do Histórico
(2026 mês a mês). Adicionado em 2026-06 (compatível — arquivo novo, não altera os existentes).

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-06-26T00:00:00Z",
  "months": [
    {
      "month": "2026-06",
      "label": "Jun",
      "run_km": 36.7,
      "run_count": 4,
      "longest_run_km": 14.0,
      "avg_pace_min_km": 5.68,
      "avg_heart_rate_bpm": 150,
      "elevation_m": 287,
      "strength_sessions": 5
    }
  ]
}
```

---

### `data/quarterly.json`
Resumo por quarter desde junho de 2024. Usado pela tabela do Histórico (2024–2025).

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-06-25T00:00:00Z",
  "quarters": [
    {
      "label": "Q3 2024",
      "period": { "start": "2024-07-01", "end": "2024-09-30" },
      "running": {
        "total_distance_km": 198.4,
        "avg_pace_min_km": 5.81,
        "total_sessions": 34,
        "longest_run_km": 14.0
      },
      "strength": {
        "total_sessions": 18
      }
    }
  ]
}
```

---

### `data/activities.json`
Atividades brutas desde junho de 2024. Não exibido diretamente na página — usado pelos agentes running-coach e strength-coach como base de análise.

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-06-25T00:00:00Z",
  "activities": [
    {
      "id": "12345678",
      "date": "2026-06-22",
      "type": "Run",
      "distance_km": 10.2,
      "duration_min": 55.4,
      "pace_min_km": 5.43,
      "avg_heart_rate_bpm": 147,
      "max_heart_rate_bpm": 168,
      "elevation_m": 42,
      "name": "Corrida matinal"
    }
  ]
}
```

**Nota:** sem campos de localização (`lat`, `lng`, `start_latlng`, `map`). Filtrados no ETL.

---

## Regras do Schema

1. **`schema_version`** obrigatório em todos os arquivos — permite detectar incompatibilidades
2. **`generated_at`** obrigatório — a página pode exibir "atualizado em X"
3. **Unidades explícitas no nome do campo** — `distance_km`, não `distance`; `pace_min_km`, não `pace`
4. **Pace em decimal** — 5.42 min/km, não "5:25". Formatação é responsabilidade da página
5. **Sem localização** — campos `lat`, `lng`, `map`, `start_latlng` nunca incluídos
6. **Mudança de schema exige novo ADR** — nunca remover ou renomear campos sem documentar

---

## Consequências

**O que essa decisão facilita:**
- Página carrega só o arquivo relevante para cada seção
- ETL e página podem evoluir independentemente enquanto o schema for respeitado
- Agentes têm acesso a dados brutos completos via `activities.json` sem expor isso na UI
- `schema_version` permite detectar incompatibilidades antes de quebrar a produção

**O que essa decisão limita:**
- ETL precisa calcular e agregar tudo — não é só dump da Strava API
- Qualquer novo KPI exige atualizar o ETL, o schema e a página

**Dívida técnica gerada:**
- Implementar validação de schema no ETL antes do commit (garante que JSON inválido nunca vai para produção)
- Definir guardrail KPI definitivo com o running-coach após análise do histórico real

---

## Referências

- ADR-001 — Arquitetura do ETL (quem gera esses arquivos)
- ADR-002 — Stack da página (quem consome esses arquivos)
