# ADR-004 — Estratégia de Atualização (GitHub Actions)

**Data:** 2026-06-25  
**Status:** Aceito  
**Autores:** Elder Gil  

---

## Contexto

O pipeline do RunForrestRun precisa rodar automaticamente todos os dias: buscar dados do Strava, gerar JSONs normalizados, e publicar a página atualizada no GitHub Pages. Todas as decisões de orquestração, falha e deploy são definidas aqui.

Requisitos:
- Dados atualizados antes do final do dia, para consulta à tarde/noite
- Credenciais protegidas em GitHub Secrets
- Falhas tratadas com retry antes de notificar
- Deploy atômico com os dados — página e dados sempre em sincronia

---

## Decisões

### 1. Horário do cron

**11h00 horário de Brasília (14h00 UTC)**

Rationale: Elder treina pela manhã. O ETL rodando às 11h garante que a atividade da manhã já está disponível na Strava API e será incluída no cálculo dos KPIs e no plano do coach. Ao consultar a página à tarde ou à noite, os dados já refletem o treino do dia.

```yaml
schedule:
  - cron: '0 14 * * *'  # 14h UTC = 11h Brasília
```

---

### 2. Estratégia de falha e retry

Se o ETL falhar (Strava API indisponível, token expirado, erro de rede):

1. O workflow aguarda **30 minutos** e tenta novamente automaticamente
2. Se a segunda tentativa também falhar, o workflow encerra com erro
3. O GitHub envia **notificação por e-mail** automaticamente (comportamento padrão do Actions para workflows com falha)
4. Os dados do dia anterior permanecem na página — nenhum dado corrompido vai ao ar

Implementado via `continue-on-error: false` e job de retry com `sleep 1800`.

---

### 3. Método de deploy

**GitHub Pages via GitHub Actions (artifact-based) — atualizado.**

Decisão original era publicar numa branch `gh-pages`. Substituída pelo método
oficial atual do GitHub Pages: o build do Vite é enviado como *Pages artifact*
(`actions/upload-pages-artifact`) e publicado por `actions/deploy-pages`, sem
branch órfã e com autenticação via OIDC.

**Rationale da mudança:** é o método recomendado pelo GitHub hoje, evita manter
uma branch de build, e o deploy fica atômico e rastreável no próprio run. A
branch `main` continua contendo exclusivamente código fonte + os JSONs de dados.

**Configuração necessária:** em *Settings → Pages → Build and deployment*, a
*Source* deve ser **GitHub Actions** (não "Deploy from a branch"). A `data/`
viaja junto: o `vite.config.js` copia os JSONs para `dist/data/` no build, então
a URL pública `/RunForrestRun/data/*.json` é servida com o app.

| Branch | Conteúdo |
|---|---|
| `main` | Código fonte (ETL, React, docs, ADRs) + JSONs versionados em `/data` |
| — | Sem branch de build; o artifact é publicado direto pelo Actions |

---

### 4. Deploy condicional

**O deploy só roda se o ETL for bem-sucedido.**

Página e dados são tratados como unidade atômica — não faz sentido republicar a página com dados desatualizados. Mudanças de layout ou componentes chegam ao ar junto com dados novos.

```yaml
jobs:
  etl:
    # busca dados, gera JSONs, faz commit
  
  deploy:
    needs: etl          # só roda se etl passar
    if: success()
    # build React + publica gh-pages
```

---

### 5. Formato do commit automático

**Formato técnico:**

```
data: update activities YYYY-MM-DD
```

Exemplo: `data: update activities 2026-06-25`

Segue a convenção de commits do projeto (definida no CLAUDE.md). O prefixo `data:` distingue commits automáticos do ETL de commits manuais de código.

---

## Fluxo Completo do Workflow

```
GitHub Actions — cron 14h UTC (11h Brasília)
    ↓
Job: etl
    1. Checkout da main
    2. Setup Python
    3. Instalar dependências (requirements.txt)
    4. Rodar strava_fetch.py (credenciais via GitHub Secrets)
       → Em caso de falha: aguarda 30min e tenta novamente
       → Em caso de segunda falha: encerra com erro → e-mail de notificação
    5. Rodar normalize.py → gera /data/*.json
    6. Commit automático: "data: update activities YYYY-MM-DD"
    7. Push para main
    ↓
Job: deploy (somente se etl = success)
    1. Checkout da main (com JSONs atualizados)
    2. Setup Node
    3. npm ci (em /site)
    4. npm run build (Vite → /site/dist/, com /data copiado para dist/data)
    5. upload-pages-artifact (site/dist) → deploy-pages
    ↓
GitHub Pages serve o artifact em https://eldergil.github.io/RunForrestRun/
```

---

## GitHub Secrets Necessários

| Secret | Descrição |
|---|---|
| `STRAVA_CLIENT_ID` | ID do app na Strava API |
| `STRAVA_CLIENT_SECRET` | Secret do app na Strava API |
| `STRAVA_REFRESH_TOKEN` | Token de refresh OAuth do atleta |

**Configuração:** GitHub → Settings → Secrets and variables → Actions → New repository secret

**Atenção:** o refresh token do Strava expira periodicamente. Monitorar e renovar manualmente quando necessário (dívida técnica registrada no ADR-001).

---

## Consequências

**O que essa decisão facilita:**
- Dados sempre atualizados antes da consulta diária, sem intervenção manual
- Falhas silenciosas evitadas — retry antes de notificar reduz ruído
- `main` limpa: sem artefatos de build misturados ao código fonte
- Atomicidade: página e dados sempre em sincronia

**O que essa decisão limita:**
- Mudanças de layout só chegam ao ar quando o ETL também rodar com sucesso
- Se o refresh token expirar, o pipeline para até renovação manual

**Dívida técnica gerada:**
- Implementar alerta proativo de expiração do refresh token (antes de quebrar)
- Considerar workflow manual (`workflow_dispatch`) para forçar atualização fora do cron

---

## Referências

- [GitHub Actions — scheduled workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
- [Vite — deploy para GitHub Pages](https://vitejs.dev/guide/static-deploy.html#github-pages)
- ADR-001 — Arquitetura do ETL
- ADR-002 — Stack da página
