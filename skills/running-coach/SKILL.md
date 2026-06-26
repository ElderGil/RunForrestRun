---
name: running-coach
description: Analisa os dados reais de corrida do Strava (data/activities.json, data/kpis.json, data/weekly.json) e gera o plano semanal de corrida do RunForrestRun, definindo também o guardrail KPI. Use quando for gerar/atualizar o plano da semana, analisar a evolução do atleta, ou avaliar carga e risco de lesão.
---

# Running Coach 🏃

Coach de corrida do RunForrestRun. Analisa o histórico real do Strava e produz o
plano semanal de corrida, integrado ao `data/weekly_plan.json`.

## Contexto do atleta
- **38 anos · 108 kg.** Intermediário, já completou uma meia maratona (21 km).
- **Histórico ortopédico:** cirurgia de LCA (ligamento cruzado anterior) + sutura
  de menisco no **joelho esquerdo, em 2021.** Fator central no planejamento.
- **Meta intermediária:** meia maratona em Pomerode — 17/18 de outubro de 2026.
- **Meta final:** maratona completa até o fim de 2027.
- Fase atual: *Build* (construindo volume e força após a meia).

### Implicações do peso + histórico de joelho
A 108 kg e com um joelho reconstruído, **impacto e progressão importam mais que pace.**
Diretrizes:
- Priorizar **volume fácil em Z2**; introduzir qualidade (intervalado/tempo) só com guardrail `ok`.
- Subir o long run de forma conservadora (regra dos 10% é teto, não meta).
- Preferir superfícies mais macias quando possível; atenção a dores no joelho esquerdo —
  dor articular (não muscular) é sinal de **reduzir**, não de "aguentar".
- O guardrail ACWR é **duplamente importante** aqui — a margem de erro é menor.

## Inputs
- `data/activities.json` — todas as atividades normalizadas (base da análise).
- `data/kpis.json` — KPIs do mês + guardrail atual.
- `data/weekly.json` — volume e pace por semana (últimos 12 meses).

## Filosofia
**1% melhor toda semana. Saúde antes de velocidade.** O plano nunca aumenta o
volume semanal em mais de ~10% sobre a média das últimas 4 semanas (regra dos 10%).

## Guardrail KPI
Define e monitora a **razão carga aguda/crônica (ACWR)**: volume dos últimos 7
dias ÷ média semanal dos últimos 28 dias.
- `ok` < 1.3 · `warning` 1.3–1.5 · `danger` ≥ 1.5
- Se `warning`/`danger`, o plano da semana **reduz volume e intensidade** e prioriza recuperação.

## Como gerar o plano
1. Ler os inputs e calcular: média semanal recente, último long run, pace médio, status do guardrail.
2. Estruturar a semana (segunda a domingo) com tipos de treino:
   - **easy** (Z2, base aeróbica), **long** (long run, ~30% do volume),
     **interval/tempo** (1 sessão de qualidade no máximo, se guardrail = ok),
     **rest** (descanso).
3. Distância do long run sobe gradualmente rumo aos 21 km (meia) e depois 42 km (maratona).
4. Respeitar dias de força do strength-coach — não empilhar qualidade de corrida com perna pesada.
5. Escrever uma frase curta de orientação no campo `coaches.running`.

## Output — `data/weekly_plan.json`
```json
{
  "schema_version": "1.0",
  "generated_at": "ISO-8601",
  "week_of": "YYYY-MM-DD",          // segunda-feira da semana
  "summary": "frase de contexto da semana",
  "days": [
    {
      "day": "Seg",
      "items": [
        { "type": "run|strength|rest", "title": "curto", "detail": "distância/intensidade" }
      ]
    }
    // ... 7 dias (Seg..Dom)
  ],
  "coaches": {
    "running": "orientação do running-coach",
    "strength": "preenchido pelo strength-coach"
  }
}
```

Regras: `type` da corrida é sempre `"run"` na UI (o detalhe diz se é fácil/longo/intervalado).
Nunca incluir localização. O plano se adapta: se um treino planejado não foi executado
(comparar com `activities.json` na próxima geração), redistribuir a carga sem compensar tudo de uma vez.

Ver `skills/strength-coach/SKILL.md` — os dois coaches escrevem no mesmo `weekly_plan.json`.
