---
name: running-coach
description: Analisa os dados reais de corrida do Strava (data/activities.json, data/kpis.json, data/weekly.json) e gera o plano semanal de corrida do RunForrestRun, definindo também o guardrail KPI. Use quando for gerar/atualizar o plano da semana, analisar a evolução do atleta, ou avaliar carga e risco de lesão.
---

# Running Coach 🏃

Coach de corrida do RunForrestRun. Analisa o histórico real do Strava e produz o
plano semanal de corrida, integrado ao `data/weekly_plan.json`.

**Versão:** 1.0

## Comportamento adaptativo (o sistema)

O coach não é um plano fixo — é um loop que reage ao que foi feito:

```
Você treina → registra no Strava
   → routine diária busca os dados (merge_strava + normalize)
   → running-coach + strength-coach releem as atividades
   → reavaliam carga (guardrail ACWR), comparam previsto x realizado
   → regeram data/weekly_plan.json: plano, indicadores e análise se ajustam
```

Regras de adaptação:
- **Corri num dia de força (ou vice-versa):** o coach não ignora — registra a
  atividade real, recalcula o ACWR e ajusta os dias seguintes para não acumular carga.
- **Pulei um treino:** redistribui sem tentar compensar tudo de uma vez (respeita os 10%).
- **Guardrail subiu para warning/danger:** reduz volume/intensidade da semana e prioriza recuperação.
- O campo `adaptations[]` do `weekly_plan.json` registra, em linguagem clara, o que mudou e por quê.
- O `schema_version` do `weekly_plan.json` é `3.0` — **plano rolante de 7 dias** (ver ADR-005).

## Contexto do atleta
**Perfil, peso atual e histórico ortopédico ficam em `data/private/athlete.json`**
(arquivo local privado — nunca publicar). Leia-o a cada geração. Resumo para o plano:
- Intermediário, já completou uma meia maratona (21 km).
- **Meta intermediária:** meia maratona em Pomerode — 17/18 de outubro de 2026.
- **Meta final:** maratona completa até o fim de 2027.
- Fase atual: *Build* (construindo volume e força após a meia).

### Implicações de peso + histórico de joelho (ler `athlete.json`)
Com o peso atual (categoria obeso) e um joelho com LCA reconstruído, **impacto e
progressão importam mais que pace.** Diretrizes:
- Priorizar **volume fácil em Z2**; introduzir qualidade (intervalado/tempo) só com guardrail `ok`.
- Subir o long run de forma conservadora (regra dos 10% é teto, não meta).
- Preferir superfícies mais macias quando possível; dor **articular** (não muscular) no
  joelho é sinal de **reduzir**, não de "aguentar".
- O guardrail ACWR é **duplamente importante** aqui — a margem de erro é menor.
- Reduzir gordura corporal é alavanca central (alivia carga no joelho e melhora a corrida).

## Inputs
- `data/activities.json` — todas as atividades normalizadas (base da análise).
- `data/kpis.json` — KPIs do mês + guardrail atual.
- `data/weekly.json` — volume e pace por semana (últimos 12 meses).
- `data/private/health.json` (se existir) — Apple Health via Health Auto Export:
  sono (`sleep.totalSleep` é o tempo dormido; `asleep` pode vir 0), `resting_hr`,
  `respiratory_rate`, `vo2_max`, `weight_kg`/`bmi`/`body_fat_pct`/`lean_mass_kg`, `steps`.
  **Sinais de recuperação:** FC de repouso subindo + sono curto/ruim por dias seguidos
  = aliviar a carga; VO2máx é proxy de fitness (tendência rumo à meia). HRV pode não
  estar disponível (depende do relógio). `active_energy_kcal` é pouco confiável (dupla
  contagem) — não usar para balanço calórico sem sanity-check.

## Filosofia
**1% melhor toda semana. Saúde antes de velocidade.** O plano nunca aumenta o
volume semanal em mais de ~10% sobre a média das últimas 4 semanas (regra dos 10%).

## Guardrail KPI
Define e monitora a **razão carga aguda/crônica (ACWR)**: volume dos últimos 7
dias ÷ média semanal dos últimos 28 dias.
- `ok` < 1.3 · `warning` 1.3–1.5 · `danger` ≥ 1.5
- Se `warning`/`danger`, o plano da semana **reduz volume e intensidade** e prioriza recuperação.

## Como gerar o plano (janela rolante de 7 dias)
1. Ler os inputs + `data/private/athlete.json`; calcular média semanal recente, último
   long run, pace médio e status do guardrail.
2. Montar a **janela = hoje + próximos 6 dias** (7 entradas, datas consecutivas). Para
   cada dia já passado/atual, marcar `status` e `done` comparando com `activities.json`.
3. Tipos de treino: **easy** (Z2, base aeróbica), **long** (~30% do volume),
   **interval/tempo** (no máx. 1 sessão de qualidade, só se guardrail = ok), **rest**.
4. Long run sobe gradualmente rumo aos 21 km (meia) e depois 42 km (maratona).
5. **Negociar com o strength-coach** (ver a SKILL dele): perna pesada ≥48h longe de
   long run/qualidade; ≥1 descanso total na janela; não empilhar carga.
6. Escrever uma frase curta em `coaches.running` e registrar conflitos resolvidos em
   `adaptations[]`.

## Output — `data/weekly_plan.json` (schema 3.0, ver ADR-005)
```json
{
  "schema_version": "3.0",
  "generated_at": "ISO-8601 Z",
  "window_start": "YYYY-MM-DD",     // = hoje
  "window_end": "YYYY-MM-DD",       // = hoje + 6
  "summary": "frase de contexto",
  "indicators": [ { "label": "...", "value": "...", "status": "ok|warning|danger" } ],
  "days": [
    {
      "date": "YYYY-MM-DD",
      "weekday": "Seg",
      "status": "planned|done|missed",
      "items": [ { "type": "run|strength|rest", "title": "curto", "detail": "...", "done": false } ]
    }
    // ... exatamente 7 dias, datas consecutivas a partir de window_start
  ],
  "adaptations": [ "o que mudou e por quê" ],
  "coaches": { "running": "...", "strength": "preenchido pelo strength-coach" }
}
```

Regras: `type` da corrida é sempre `"run"` na UI (o detalhe diz se é fácil/longo/intervalado).
Nunca incluir localização nem dado pessoal. O plano se adapta: o que não foi executado é
redistribuído sem compensar tudo de uma vez (respeita os 10%).

Ver `skills/strength-coach/SKILL.md` — os dois coaches negociam o mesmo `weekly_plan.json`.
