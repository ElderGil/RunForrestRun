# Apple Health sem app pago: Atalho diário

O Health Auto Export parou de exportar sozinho quando o trial acabou (06/2026). Desde
28/06/2026 o `data/private/health.json` não recebe sono, FC de repouso nem VO2máx, e os
coaches decidem a recuperação só com Strava e guardrails. Este guia monta a mesma ponte
com o app **Atalhos** da Apple, de graça.

O lado do Mac já está pronto: `etl/merge_health.py` acha o arquivo no iCloud Drive e
lê o formato abaixo (`parse_shortcuts_export`). Falta só montar o Atalho no iPhone.

## O arquivo que o Atalho precisa gravar

Um JSON por dia, num nome que comece com `HealthMetrics` (é o que o ETL procura),
salvo em qualquer pasta do iCloud Drive. Exemplo: `iCloud Drive/Atalhos/HealthMetrics.json`.

```json
{
  "date": "2026-11-11",
  "resting_hr": 52,
  "hrv_ms": 38,
  "vo2_max": 41.5,
  "steps": 8400,
  "sleep": { "totalSleep": 6.9 }
}
```

- Qualquer campo pode faltar. O ETL guarda só o que vier.
- `sleep.totalSleep` é em **horas** (6.9 = 6h54).
- Campos aceitos: `resting_hr`, `hrv_ms`, `respiratory_rate`, `vo2_max`, `steps`,
  `active_energy_kcal`, `weight_kg`, `body_fat_pct`, `lean_mass_kg`, `bmi`. Os de
  composição corporal ficam só no arquivo privado, nunca na página.
- Sobrescrever o mesmo arquivo todo dia funciona: o ETL mescla por data e não perde o
  histórico.

## Montando o Atalho

Os nomes das ações podem variar um pouco entre versões do iOS.

1. **Atalhos → +** (novo atalho), nome `RunForrestRun Health`.
2. **Data**: ação "Data Atual" e depois "Formatar Data" com formato personalizado
   `yyyy-MM-dd`. Guarde numa variável `Hoje`.
3. Para cada métrica, uma ação **"Encontrar Amostras de Saúde"**:
   - *Frequência Cardíaca em Repouso*: data de início "nos últimos 1 dias", ordenar por
     data de início, mais recente primeiro, limite 1. Pegue o valor.
   - *Variabilidade da Frequência Cardíaca*: igual. Se vier vazio, o relógio não manda VFC
     (ver abaixo).
   - *VO2 Máx.*: últimos 30 dias, mais recente, limite 1.
   - *Passos*: "hoje" ou "ontem", sem limite, e depois "Calcular Estatísticas → Soma".
   - *Análise do Sono*: início "nas últimas 18 horas"; filtre os valores de sono (Principal,
     Profundo, REM), pegue a **Duração** de cada um, "Calcular Estatísticas → Soma" e
     divida por 3600 para ter horas.
4. Ação **"Dicionário"** com as chaves do JSON acima (`date` = `Hoje`, `resting_hr`,
   `hrv_ms`, `vo2_max`, `steps`) e um dicionário interno `sleep` com `totalSleep`.
5. Ação **"Salvar Arquivo"**: destino iCloud Drive, caminho `Atalhos/HealthMetrics.json`,
   **desligue** "Perguntar Onde Salvar" e **ligue** "Substituir se o arquivo existir".
6. Rode uma vez à mão e confira se o arquivo aparece no Mac, em
   `~/Library/Mobile Documents/com~apple~CloudDocs/Atalhos/`.

## Agendando

**Atalhos → Automação → + → Hora do Dia**, às **10:30** (antes da routine das ~11h),
diariamente, **Executar Imediatamente**, ação "Executar Atalho → RunForrestRun Health".

Limitação conhecida: o iOS só deixa ler o HealthKit com o iPhone desbloqueado. Se o
telefone estiver bloqueado às 10:30, a automação pode falhar naquele dia. Usar o iPhone
nesse horário costuma bastar. Se falhar com frequência, um gatilho como "Ao parar o
alarme" ou "Ao abrir o app Saúde" roda com o telefone em uso.

## Conferindo no Mac

```bash
python3 etl/merge_health.py
```

Deve aparecer `Health (Atalho caseiro): HealthMetrics.json -> 1 dia(s)`. Se continuar
lendo o `HealthAutoExport-...json` antigo, apague ou mova esse arquivo da nuvem: o ETL
pega o export **mais recente** e o do Atalho passa a ser ele.

## VFC (HRV) do Amazfit

A VFC não chega ao Apple Health hoje. É configuração do relógio e do app Zepp, não do
pipeline:

1. No Zepp: **Perfil → (relógio) → Monitoramento de saúde**, ligue a medição de estresse
   ou VFC contínua, se o modelo oferecer.
2. No Zepp: **Perfil → Adicionar contas → Apple Saúde**, e no app Saúde do iPhone em
   **Compartilhamento → Apps → Zepp**, libere a escrita de "Variabilidade da Frequência
   Cardíaca".
3. Confira em **Saúde → Coração → Variabilidade da Frequência Cardíaca** se aparecem
   pontos novos depois de uma noite.

Alguns modelos Amazfit não gravam VFC no Apple Health, mesmo medindo no relógio. Nesse
caso o campo `hrv_ms` fica vazio e os coaches seguem com FC de repouso e sono, que já
cobrem o sinal de recuperação.
