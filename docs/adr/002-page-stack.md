# ADR-002 — Stack da Página

**Data:** 2026-06-25  
**Status:** Aceito  
**Autores:** Elder Gil  

---

## Contexto

A página RunForrestRun precisa ser servida como arquivos estáticos no GitHub Pages. O conteúdo é orientado a dados: KPIs com tooltips explicativos, gráficos interativos de evolução (pace + volume), tabs para o plano semanal e filtros de período. O design é mobile-first.

A decisão define qual tecnologia constrói a interface — impacta diretamente a qualidade do código, a manutenibilidade e o que a página demonstra tecnicamente.

---

## Opções Consideradas

### Opção A — React + Vite + Recharts ✅ Escolhida

React como framework de UI, Vite como bundler e ferramenta de build, Recharts como biblioteca de gráficos nativa para React.

**Prós:**
- Componentes reutilizáveis: `<KPICard>`, `<WeeklyPlan>`, `<EvolutionChart>` escritos uma vez, usados em múltiplas seções
- Estado de UI limpo: filtros de período, tabs e tooltips gerenciados com `useState` — sem manipulação manual de DOM
- Recharts é responsivo por padrão e animado — integra naturalmente com estado React
- Vite produz build estático otimizado, compatível com GitHub Pages sem configuração adicional
- Stack mais valorizada no mercado — demonstra domínio relevante
- Hot reload durante desenvolvimento

**Contras:**
- Requer build step (resolvido: GitHub Actions já roda no pipeline, adicionar `npm run build` é trivial)
- Mais complexo para quem quer só "abrir o index.html" — arquivo fonte não é o arquivo servido

---

### Opção B — HTML puro + Chart.js

HTML, CSS e JavaScript sem framework. Chart.js para gráficos.

**Prós:**
- Zero build step — o arquivo fonte é o arquivo servido
- Mais simples de inspecionar no browser

**Contras:** ❌ Descartada
- Sem componentes: qualquer mudança no card de KPI exige edição em múltiplos lugares
- Estado de UI (filtros, tabs) vira manipulação manual de DOM — código difícil de manter
- Chart.js requer configuração imperativa verbose; não integra naturalmente com estado
- Não demonstra domínio de stack moderna

---

## Decisão

**React + Vite + Recharts.**

O build é gerado pelo GitHub Actions e publicado no GitHub Pages via `gh-pages` branch. O código fonte fica em `/site/` e o build em `/site/dist/`.

---

## Estrutura do Projeto React

```
site/
├── index.html
├── vite.config.js
├── package.json
├── src/
│   ├── main.jsx              # Entry point
│   ├── App.jsx               # Layout principal + navegação
│   ├── components/
│   │   ├── Hero.jsx          # Resumo do mês atual
│   │   ├── RunningSection.jsx # KPIs + gráfico de corrida
│   │   ├── StrengthSection.jsx# KPIs de força
│   │   ├── HistorySection.jsx # Visão por quarter
│   │   ├── WeeklyPlan.jsx    # Plano semanal (tab)
│   │   ├── KPICard.jsx       # Card reutilizável com legenda
│   │   └── EvolutionChart.jsx # Gráfico pace + volume
│   ├── data/
│   │   └── loaders.js        # Funções para carregar os JSONs de /data/
│   └── styles/
│       └── index.css         # Tokens de design (cores, tipografia)
```

---

## Decisões de Design System

- **Cores:** gradientes roxo → pink/magenta → laranja como acentos; fundo white/off-white
- **Tipografia:** Inter ou similar sans-serif, bold para títulos e KPIs
- **Responsividade:** mobile-first via CSS Grid e Flexbox — sem biblioteca de UI externa
- **Gráficos:** Recharts `<ComposedChart>` para pace + volume no mesmo eixo
- **Sem biblioteca de UI** (Chakra, MUI, etc.) — CSS customizado mantém o visual único e sem overhead

---

## Integração com o ETL

A página consome os JSONs gerados pelo ETL (ADR-001) via fetch em `loaders.js`. Os arquivos ficam em `/data/` na raiz do repositório e são acessíveis pela URL pública do GitHub Pages.

```js
// loaders.js
export const loadKPIs = () => fetch('/data/kpis.json').then(r => r.json())
export const loadWeekly = () => fetch('/data/weekly.json').then(r => r.json())
export const loadQuarterly = () => fetch('/data/quarterly.json').then(r => r.json())
```

---

## Consequências

**O que essa decisão facilita:**
- Componentes reutilizáveis tornam a adição de novos KPIs trivial
- Estado React gerencia filtros e tabs sem código adicional complexo
- Recharts torna os gráficos responsivos por padrão
- A stack demonstra competência técnica moderna

**O que essa decisão limita:**
- Não é possível "abrir o index.html" diretamente — precisa do build ou de `npm run dev`
- Qualquer colaborador precisa de Node instalado para contribuir

**Dívida técnica gerada:**
- Configurar `vite.config.js` com `base` correto para o GitHub Pages (ex: `/RunForrestRun/`)
- Garantir que os caminhos dos JSONs funcionem tanto em desenvolvimento quanto em produção

---

## Referências

- [Vite — Static Site Deployment para GitHub Pages](https://vitejs.dev/guide/static-deploy.html#github-pages)
- [Recharts — Documentação](https://recharts.org/)
- ADR-001 — Arquitetura do ETL (fonte dos JSONs consumidos pela página)
- ADR-003 — Schema dos dados (contrato dos JSONs)
