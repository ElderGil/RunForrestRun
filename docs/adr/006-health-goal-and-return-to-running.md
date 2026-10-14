# ADR-006: Objetivo de saúde e protocolo de volta à corrida

**Status:** Aceito · 2026-10-14
**Substitui em parte:** ADR-005 (a meta que orienta o running-coach)

## Contexto

O projeto nasceu com duas metas de prova: a meia maratona de Pomerode (17/10/2026) e uma
maratona até o fim de 2027. Em outubro de 2026 a situação real era outra:

1. **Pausa de corrida.** A última corrida foi em 20/09/2026. Foram cerca de 3 semanas sem
   correr, por agenda, sem dor ou lesão. A força continuou (2 a 3 sessões por semana).
2. **Meta trocada.** O atleta não vai correr a meia de Pomerode. O objetivo passa a ser
   saúde: perder peso e manter corrida e força com constância. A maratona fica como
   horizonte distante, sem data.
3. **Guardrail cego na volta.** A ACWR (`etl/normalize.py`) divide os km dos últimos 7 dias
   pela média semanal dos últimos 28. Depois de uma pausa, a média de 28 dias contém quase
   só a própria semana atual. A primeira corrida de 3 km dá 3 ÷ 0,75 = 4,0, que é
   `danger`. Pela regra dos coaches, isso obrigaria descanso logo no primeiro treino.
4. **Joelho.** O histórico do joelho é antigo (detalhes só em `data/private/athlete.json`).
   Desde fev/2026 o atleta faz musculação com bastante volume de perna, e a musculatura
   está adaptada. As restrições de amplitude por padrão ficaram mais conservadoras do que
   o necessário.
5. **Dado pessoal nas skills.** As `SKILL.md` (repo público) voltaram a citar categoria de
   peso, cirurgia e cargas, contrariando o item 4 do ADR-005.

## Decisão

### 1. Metas

- **Principal:** saúde, com perda de peso como maior objetivo. Os números (peso atual,
  meta) ficam só em `data/private/athlete.json`.
- **Meio:** constância de corrida e força, sem lesão.
- **Horizonte:** maratona, sem data. Não orienta o plano.
- Nenhuma prova aparece na página, no README ou nos textos públicos dos coaches.

### 2. Protocolo de volta à corrida (running-coach)

Ativa quando o atleta passou **14 dias ou mais sem correr**, e vale até ele completar
**4 semanas seguidas com corrida**:

- 2 a 3 corridas fáceis por semana, 20 a 30 min, em Z2. Alternar corrida e caminhada é
  permitido.
- Primeira semana com 50 a 60% do volume semanal de antes da pausa.
- Sem long run e sem treino de qualidade (intervalado ou tempo) durante o protocolo.
- Aumento máximo de ~10% por semana sobre a semana anterior (não sobre a média de 4).
- Dor articular interrompe, como em qualquer fase.

### 3. Perda de peso no plano

- **Corrida:** frequência e minutos em Z2 pesam mais que pace ou distância.
- **Bike:** pedal fácil conta como cardio de baixo impacto em dias sem corrida.
- **Força:** manter o programa A/B/C completo para preservar massa magra durante a perda
  de peso.
- O plano público nunca mostra peso, IMC ou meta numérica.

### 4. Status `rebuilding` na ACWR

`acute_chronic_ratio` ganha um quinto status. Ele aparece quando houve corrida nos últimos
7 dias, mas **menos de 3 das 3 semanas anteriores** (dias 7 a 27) tiveram alguma corrida.
Nesse caso a média de 28 dias não representa a base do atleta e a razão fica inflada.

- `rebuilding` **não** obriga descanso. Durante o protocolo, os freios são o próprio
  protocolo (volume curto e fácil) e o `load_guardrail`, que compara o esforço com o
  histórico do atleta e continua válido.
- O valor da razão continua sendo calculado, mas a página mostra "—" e explica o motivo.
- Com corrida esparsa (uma a cada duas semanas), o status também aparece. É esperado:
  nesse padrão a ACWR não tem sentido, e o protocolo cuida da progressão.

### 5. Fase no plano (`weekly_plan.json`)

Campo opcional `phase` no schema 3.0. É aditivo, então planos sem ele continuam válidos:

```jsonc
"phase": { "label": "Volta à corrida", "detail": "semana 1 de 4" }
```

O hero da página mostra a fase no lugar da contagem regressiva para uma prova.

### 6. Joelho

- Amplitude completa liberada por padrão; limitar só com dor articular.
- Mantém: dor articular reduz, nunca progride; posterior forte como proteção.
- A regra de perna pesada ≥48h longe de long run e qualidade fica como princípio de
  recuperação, não como restrição médica.

### 7. Texto público

As `SKILL.md`, `coaches.json` e o plano apontam para `data/private/` em vez de citar peso,
cirurgia ou cargas. Um teste de contrato passa a varrer também `coaches.json` e as
`SKILL.md`. A página e o README deixam de usar emoji.

## Consequências

- `etl/normalize.py`, `tests/test_etl.py` e `tests/test_schema.py` mudam para o novo status
  e o campo `phase`.
- `skills/running-coach/SKILL.md` e `skills/strength-coach/SKILL.md` trocam as metas de
  prova pelo objetivo de saúde e ganham o protocolo de volta.
- `site/`: hero lê `plan.phase`; título e descrição da página mudam; emoji removidos.
- PRD vai para a versão 1.1; CLAUDE.md e ADR-005 recebem nota de atualização.
- Quando o protocolo terminar (4 semanas seguidas), a ACWR volta a ser o guardrail
  principal de corrida sem nenhuma mudança de código.
