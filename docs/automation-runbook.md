# Runbook — Atualização diária do RunForrestRun

Este é o procedimento que o **agente agendado** (routine diária, ~11h BRT; cron 11:00 local com até ~14 min de jitter)
executa. Não usa Secrets do Strava: a busca é feita pela **conexão Strava do Claude**
(MCP). O agente roda "do zero" a cada dia, então segue estes passos exatamente.

## Pré-requisitos
- Repositório `ElderGil/RunForrestRun` clonado, na branch `main`.
- Python 3 disponível. O ETL só usa a biblioteca padrão; os testes usam o venv do projeto
  (`.venv/`, gitignored). Se ele não existir:
  `python3 -m venv .venv && .venv/bin/pip install -r etl/requirements.txt`.
- Conexão Strava do Claude ativa (ferramentas `list_activities`, `get_activity_performance`).

## Passos

1. **Descobrir a última atividade já armazenada.**
   Ler a maior `start_date_local` em `data/activities_raw.json`.

2. **Buscar atividades novas no Strava** (`list_activities`, `range_start` = dia da
   última atividade, ordenado por mais recente, **sem** `use_preferred_units`: o store
   guarda metros e m/s). Salvar a resposta em `/tmp/strava_new.json`.
   **Sem atividade nova não encerra:** pular a mesclagem do passo 4 (o `normalize.py` e o
   `merge_health.py` rodam do mesmo jeito) e seguir para o passo 5. A janela precisa
   deslizar todo dia, e um dia sem treino também é informação (vira `missed`).

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

   > `merge_health.py` acha o JSON mais recente do app **Health Auto Export** (iOS) em
   > qualquer nuvem montada no Mac — iCloud Drive **ou** Google Drive/Dropbox/OneDrive
   > (`~/Library/CloudStorage/...`) — e grava `data/private/health.json` (privado).
   > O Health Auto Export parou de exportar em 06/2026 (fim do trial). A ponte gratuita é
   > um Atalho do iPhone gravando `HealthMetrics.json` no iCloud Drive
   > ([guia](apple-health-shortcut.md)). Sem arquivo novo, o comando é um no-op e a
   > routine segue normal.

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
   .venv/bin/python -m pytest tests/ -q   # venv do projeto; o python3 do Homebrew não tem pytest
   git add data/
   git commit -m "data: daily update"   # sem $(...) — substituição de comando trava o job agendado em permissão
   git push
   ```
   O push em `data/**` dispara o workflow `pages.yml`, que rebuilda e publica o site.

## Em caso de falha
- Strava indisponível: aguardar e tentar de novo; se persistir, encerrar sem commit
  (os dados do dia anterior permanecem no ar — nada corrompido vai à produção).
- Token/conexão expirada: registrar no resumo do run para renovação manual.
- **Sessão abriu em plan mode:** a routine não consegue escrever nem commitar. Encerrar
  e relatar. A causa é `permissions.defaultMode: "plan"` em `~/.claude/settings.json`,
  que vale também para as sessões agendadas. Foi o que parou a publicação de 17/10 a
  10/11/2026, com todas as execuções marcadas como "succeeded".

## Alerta de dado parado
O workflow `.github/workflows/freshness.yml` roda todo dia às 21h BRT e **falha** se
`data/weekly_plan.json` não começar em hoje ou ontem. Falha de workflow agendado gera
e-mail do GitHub, então qualquer motivo de parada (conexão do Strava expirada, Mac
desligado, plan mode, erro no meio do pipeline) vira aviso no mesmo dia. A página também
mostra um aviso no plano quando a janela está atrasada.
