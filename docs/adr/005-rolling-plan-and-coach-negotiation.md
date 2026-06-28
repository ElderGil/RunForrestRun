# ADR-005 — Plano rolante de 7 dias + negociação dos coaches

**Status:** Aceito · 2026-06-28
**Contexto decidido com o atleta** (ver memória do projeto).

## Contexto

O `weekly_plan.json` (schema 2.0) modelava uma **semana fixa** (segunda a domingo,
campo `week_of` + dias `Seg..Dom`). Dois problemas surgiram no uso real:

1. **Horizonte curto.** No domingo (último dia da semana) não havia plano para o dia
   seguinte. Como o atleta treina **de manhã**, ele abria a página sem saber o que fazer.
2. **Geração tardia.** A routine diária (11:08 BRT) só criava a semana nova "na segunda" —
   depois do treino matinal. A segunda-feira nascia em branco.

Além disso, os coaches (running + strength) escreviam blocos de texto separados; os
`days[]` não eram fruto de uma negociação explícita entre eles, e o programa de força
A/B/C vivia transcrito em markdown, não como artifact consultável.

## Decisão

### 1. Plano rolante de 7 dias (schema 3.0)

O plano deixa de ser uma semana fixa e passa a ser uma **janela móvel = hoje + próximos
6 dias**. Não há mais fronteira de semana, então nunca falta "amanhã".

```jsonc
{
  "schema_version": "3.0",
  "generated_at": "ISO-8601 Z",
  "window_start": "YYYY-MM-DD",   // = hoje
  "window_end": "YYYY-MM-DD",     // = hoje + 6
  "summary": "frase de contexto",
  "indicators": [ { "label": "...", "value": "...", "status": "ok|warning|danger" } ],
  "days": [
    {
      "date": "YYYY-MM-DD",
      "weekday": "Seg",            // rótulo pt-BR (derivável da data)
      "status": "planned|done|missed",
      "items": [
        { "type": "run|strength|rest", "title": "...", "detail": "...", "done": false }
      ]
    }
    // ... exatamente 7 dias, datas consecutivas a partir de window_start
  ],
  "adaptations": [ "o que mudou e por quê" ],
  "coaches": { "running": "...", "strength": "..." }
}
```

**Lógica diária (sem caso especial de fronteira):** a cada execução a routine *desliza*
a janela — início = hoje, gera o novo dia da ponta (hoje+6), marca `status`/`done` do que
foi realizado e re-negocia os dias planejados. O horário do job permanece 11:08; como a
janela sempre carrega 6 dias à frente, o "amanhã" já está visível de manhã.

### 2. Negociação equilibrada dos coaches

Sem hierarquia fixa. A cada geração:
1. **running-coach** rascunha os dias de corrida (tipo/intensidade/distância) pela meta
   (meia Pomerode out/2026), guardrail ACWR e carga recente.
2. **strength-coach** rascunha os dias de força a partir do **programa A/B/C fixo**
   (`data/private/strength_program.json`), respeitando a recuperação.
3. **Passo de merge** concilia conflitos dia a dia com regras:
   - ≤1 sessão dura por dia (força leve de superiores pode coexistir com corrida fácil);
   - perna pesada **≥48h** de distância de long run / treino de qualidade (antes e depois);
   - **≥1 descanso total** na janela;
   - carga combinada não pode estourar o guardrail ACWR.
4. Saída: um `days[]` integrado + nota curta de cada coach + `adaptations[]` explicando os
   conflitos resolvidos.

### 3. Programa de força como base fixa (artifact)

O A/B/C do Coach Ernesto é **base fixa**, executada em sequência. Os coaches **não trocam
nem inventam** exercícios — só reduzem série/reps/carga, limitam amplitude ou pausam um
item, sempre com justificativa. A transcrição + análise vivem em
`data/private/strength_program.json` (privado).

### 4. Dados pessoais fora do público

Perfil, peso e histórico médico saem das SKILL.md (repo público) e passam a viver em
`data/private/` (gitignored; o build do site não copia subpastas de `data/`). Os coaches
leem esses arquivos **localmente**; a página só mostra o plano derivado, sem dado pessoal.

## Consequências

- **Quebra de schema** (2.0 → 3.0): atualizar frontend (`WeeklyPlan.jsx`), o teste de
  contrato (`tests/test_schema.py`), as SKILL.md dos coaches, a SKILL da scheduled-task e o
  `docs/automation-runbook.md`.
- O frontend passa a renderizar uma lista de 7 dias com datas reais, destacando **hoje** e
  **amanhã**, no lugar do grid fixo Seg–Dom.
- A periodização semanal "pura" (Mon–Sun) é trocada pela janela rolante; métricas semanais
  para análise continuam em `weekly.json` (inalterado).
