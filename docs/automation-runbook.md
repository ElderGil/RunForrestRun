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
   python etl/merge_health.py   # sono/recuperação/peso do Apple Health (no-op se não houver export)
   ```

   > `merge_health.py` lê o JSON mais recente que o app **Health Auto Export** (iOS)
   > deposita no iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/HealthAutoExport/`)
   > e grava `data/private/health.json` (privado). Se a ponte ainda não estiver
   > configurada no iPhone, o comando é um no-op e a routine segue normal.

5. **Reavaliar como coach e regerar o plano rolante.** Ler `skills/running-coach/SKILL.md`,
   `skills/strength-coach/SKILL.md` e os artifacts privados `data/private/athlete.json` e
   `data/private/strength_program.json`. Com base nos dados atualizados
   (`data/activities.json`, `data/kpis.json`, `data/weekly.json`), **regerar
   `data/weekly_plan.json`** no **schema 3.0 — janela rolante de 7 dias (ADR-005)**:
   - Janela = `window_start` (hoje) … `window_end` (hoje+6); 7 dias consecutivos com
     `date`, `weekday`, `status` e `items`. A janela **desliza todo dia** — não há mais
     "criar a semana na segunda".
   - Marcar `status: done` / `done: true` nos dias já realizados (comparar com `activities.json`).
   - **Negociação dos coaches:** A/B/C em sequência sem trocar exercícios (só reduzir
     série/carga, limitar amplitude ou pausar com justificativa); perna pesada ≥48h de
     long run/qualidade; ≥1 descanso total; carga dentro do guardrail ACWR.
   - Registrar em `adaptations[]` o que mudou e por quê; atualizar `indicators`,
     `coaches.running` e `coaches.strength`.
   - **Nunca** expor dados pessoais (peso, idade, medidas, histórico médico) no
     `weekly_plan.json` — eles vivem só em `data/private/` (gitignored).

6. **Validar e commitar:**
   ```bash
   python -m pytest tests/ -q
   git add data/
   git commit -m "data: daily update"   # sem $(...) — substituição de comando trava o job agendado em permissão
   git push
   ```
   O push em `data/**` dispara o workflow `pages.yml`, que rebuilda e publica o site.

## Em caso de falha
- Strava indisponível: aguardar e tentar de novo; se persistir, encerrar sem commit
  (os dados do dia anterior permanecem no ar — nada corrompido vai à produção).
- Token/conexão expirada: registrar no resumo do run para renovação manual.
