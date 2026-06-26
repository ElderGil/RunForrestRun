# Runbook — Atualização diária do RunForrestRun

Este é o procedimento que o **agente agendado** (routine diária, 11h BRT / 14h UTC)
executa. Não usa Secrets do Strava: a busca é feita pela **conexão Strava do Claude**
(MCP). O agente roda "do zero" a cada dia, então segue estes passos exatamente.

## Pré-requisitos
- Repositório `ElderGil/RunForrestRun` clonado, na branch `main`.
- Python 3 disponível (`pip install -r etl/requirements.txt` se necessário).
- Conexão Strava do Claude ativa (ferramentas `list_activities`, `get_activity_performance`).

## Passos

1. **Descobrir a última atividade já armazenada.**
   Ler a maior `start_date_local` em `data/activities_raw.json`.

2. **Buscar atividades novas no Strava** (`list_activities`, `range_start` = dia da
   última atividade, ordenado por mais recente). Salvar a resposta em
   `/tmp/strava_new.json`. Se não houver nada novo, encerrar sem commit.

3. **Enriquecer corridas com HR.** Para cada atividade `Run` nova, chamar
   `get_activity_performance` e montar um mapa
   `{ "<id>": {"average_heartrate": x, "max_heartrate": y} }` em `/tmp/strava_hr.json`.
   (A lista do Strava não traz HR; só o detalhe traz.)

4. **Mesclar no store e normalizar:**
   ```bash
   python etl/merge_strava.py /tmp/strava_new.json /tmp/strava_hr.json
   python etl/normalize.py
   ```

5. **Reavaliar como coach e regerar o plano.** Ler `skills/running-coach/SKILL.md` e
   `skills/strength-coach/SKILL.md` e, com base nos dados atualizados
   (`data/activities.json`, `data/kpis.json`, `data/weekly.json`), **regerar
   `data/weekly_plan.json`** (schema 2.0):
   - Atualizar `indicators` (corridas na semana, guardrail ACWR, FC média).
   - Marcar `done: true` nos dias já realizados; ajustar os dias futuros.
   - Se uma atividade saiu do previsto (ex.: corrida em dia de força), registrar em
     `adaptations[]` o que mudou e por quê, e recalcular a carga.
   - Atualizar `coaches.running` e `coaches.strength`.
   - No início de uma nova semana (segunda), criar o plano da semana seguinte.
   - **Nunca** expor dados pessoais (peso, histórico médico) no `weekly_plan.json` —
     isso é contexto interno das skills, não conteúdo de página.

6. **Validar e commitar:**
   ```bash
   python -m pytest tests/ -q
   git add data/
   git commit -m "data: update activities $(date -u +%Y-%m-%d)"
   git push
   ```
   O push em `data/**` dispara o workflow `pages.yml`, que rebuilda e publica o site.

## Em caso de falha
- Strava indisponível: aguardar e tentar de novo; se persistir, encerrar sem commit
  (os dados do dia anterior permanecem no ar — nada corrompido vai à produção).
- Token/conexão expirada: registrar no resumo do run para renovação manual.
