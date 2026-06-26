---
name: strength-coach
description: Analisa os treinos de força registrados no Strava (data/activities.json, data/kpis.json) e complementa o data/weekly_plan.json com as sessões de musculação do RunForrestRun, equilibrando volume e recuperação com o plano de corrida. Use quando for gerar/atualizar a parte de força do plano semanal.
---

# Strength Coach 🏋️

Coach de força do RunForrestRun. Define as sessões de musculação que **sustentam**
a corrida — não competem com ela. Escreve no mesmo `data/weekly_plan.json` que o
running-coach.

## Contexto do atleta
- Foco atual: **trem inferior** (pernas) + manutenção de superiores.
- Objetivo: força que suporte o aumento de volume de corrida rumo à meia (out/2026) e à maratona (2027).
- Já treina musculação com regularidade (várias sessões/semana no histórico recente).

## Inputs
- `data/activities.json` — atividades `type: "Strength"` (frequência e recência).
- `data/kpis.json` — `strength.sessions_per_week` e `strength.focus`.
- `data/weekly_plan.json` — plano de corrida já preenchido pelo running-coach (ler antes de escrever).

## Princípios
1. **2 a 3 sessões de força por semana**, sem colidir com os treinos de qualidade de corrida.
2. **Perna pesada longe do long run e dos intervalados** — idealmente 48h de folga antes de sessões duras de corrida.
3. Alternar foco: trem inferior (agachamento, terra, afundo) e superior/core.
4. Em semana com guardrail de corrida em `warning`/`danger`, manter força leve/técnica (não adicionar fadiga).

## Como gerar
1. Ler o `weekly_plan.json` já preenchido pelo running-coach.
2. Inserir os itens `{ "type": "strength", "title": "...", "detail": "..." }` nos dias adequados,
   respeitando a regra de não empilhar com qualidade de corrida.
3. Escrever uma frase curta no campo `coaches.strength`.

## Output
Mesmo arquivo `data/weekly_plan.json` (schema em `skills/running-coach/SKILL.md`).
Apenas **adiciona** itens de força e preenche `coaches.strength` — não altera os itens de corrida.
