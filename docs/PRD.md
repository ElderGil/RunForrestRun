# PRD — RunForrestRun

**Versão:** 1.1  
**Data:** 2026-06-25 · revisado em 2026-10-14 (objetivos, ver ADR-006)  
**Status:** Aprovado  

---

## 1. Visão Geral

RunForrestRun é uma página pública no GitHub Pages que documenta o treino do Elder, conduzido por dois coaches de IA (corrida e força), com foco em saúde. O projeto une dados reais do Strava com visualizações claras, decisões de engenharia documentadas e planos gerados por agentes de IA — tudo visível, tudo explicado.

**Filosofia central:** 1% melhor toda semana.

---

## 2. Objetivos

| Objetivo | Prazo |
|---|---|
| Saúde: perder peso (números só em `data/private/`) | Contínuo |
| Constância de corrida e força, sem lesão | Contínuo |
| Volta gradual à corrida após pausa (protocolo do ADR-006) | Out–nov/2026 |
| Maratona completa | Horizonte distante, sem data |

> Revisão de 2026-10-14: a meia de Pomerode (17/10/2026) e o prazo de 2027 para a maratona
> saíram. Motivo e regras novas em [ADR-006](adr/006-health-goal-and-return-to-running.md).

---

## 3. Público-Alvo

A página é aberta a qualquer visitante. O design deve funcionar simultaneamente para:

- **Público técnico** (devs, recrutadores): aprecia a arquitetura, os dados, as decisões documentadas, a qualidade da engenharia
- **Público geral** (corredores, amigos): compreende os KPIs, acompanha a evolução, entende o contexto sem precisar de conhecimento técnico

O projeto demonstra habilidades pelo que exibe — não pelo que declara.

---

## 4. Estrutura da Página

Página única com scroll. Sem subpáginas. Navegação interna por âncora.

### 4.1 Seções (em ordem)

**Hero — Resumo do Mês Atual**
- Mês em curso com métricas principais: km totais, número de treinos, pace médio
- Frase visível com a fase atual do plano (ex.: volta à corrida), lida de `weekly_plan.json`
- Tom: contexto antes dos números

**Corrida**
- KPIs de corrida com legenda explicando por que cada um importa
- Gráfico de evolução: pace + volume (km) por semana/mês
- Guardrail KPI: definido pelo running-coach com base nos dados reais do Strava (ver seção 7)
- Período exibido: configurável (padrão: últimos 6 meses)

**Força**
- KPIs de treino de força
- Foco em treinos de academia registrados no Strava
- Contexto: como o treino de força complementa a corrida

**Histórico**
- Visão agregada por quarter (Q1, Q2, Q3, Q4)
- Referência para os coaches; não é o foco visual principal
- Sem detalhamento por atividade individual
- Sem exibição de localização de treinos

**Plano Semanal (tab dedicada)**
- Aba separada dentro da página
- Calendário unificado: corrida + força + descanso
- Plano gerado semanalmente pelos agentes running-coach e strength-coach
- Adaptado automaticamente quando treinos não forem executados conforme planejado
- Distinção visual clara entre tipos de treino (corrida, força, descanso)

---

## 5. KPIs Monitorados

Cada KPI exibido na página deve ter uma legenda curta explicando por que é acompanhado.

### Corrida
| KPI | Legenda (por que acompanhar) |
|---|---|
| Pace médio (min/km) | Indicador direto de velocidade e evolução de performance |
| Distância semanal (km) | Controle de carga — base para periodização segura |
| Frequência cardíaca média | Eficiência cardiovascular: menos esforço para o mesmo pace = evolução real |
| FC máxima | Intensidade real dos treinos |
| Elevação acumulada (m) | Força e resistência muscular em terreno variado |
| Tempo em zona de FC | Distribuição de intensidade — polarização do treino |
| Long run mais longo | Resistência aeróbica; base para distâncias maiores |
| Consistência (treinos/semana) | Disciplina — o KPI mais importante a longo prazo |
| Guardrail KPI | A definir pelo running-coach (ex: razão carga aguda/crônica, FC repouso, HRV) |

### Força
| KPI | Legenda |
|---|---|
| Frequência semanal (sessões) | Consistência do treino complementar |
| Volume por grupo muscular | Equilíbrio entre trem inferior e superior |
| Integração com ciclo de corrida | Força e corrida como sistema — não competindo |

---

## 6. Identidade Visual

**Modo:** Light mode como padrão  
**Responsividade:** Mobile-first — a página deve funcionar bem em telas pequenas  
**Estilo:** Clean, editorial, premium — sem gamificação  
**Referências:** AR Virtual Fitness Coach (Behance) + BytePal/NutriPal (Behance)

### Diretrizes visuais
- Fundo branco/off-white como base
- Gradientes vibrantes (roxo → pink/magenta → laranja) como elementos de acento — não como fundo
- Tipografia bold, sem serifa, hierarquia clara
- Cards com sombra sutil para KPIs em destaque
- Gráficos com área preenchida em gradiente, fluidos
- Seções alternando peso visual (leve / acentuado)
- Sem badges, troféus ou elementos de gamificação
- Sem comparações com outros atletas
- Sem dados de peso corporal

---

## 7. Agentes e Skills

### running-coach
- Analisa dados reais do Strava (histórico desde junho de 2024)
- Define o **guardrail KPI** do projeto com base nos dados (saúde > velocidade)
- Gera plano de treino semanal de corrida
- Ajusta o plano se treinos não forem executados

### strength-coach
- Analisa atividades de academia registradas no Strava
- Gera plano de treino de força complementar ao calendário de corrida
- Equilibra volume e recuperação entre modalidades

Ambos os planos são exibidos integrados no **Plano Semanal**.

---

## 8. Dados

- **Fonte:** Strava API
- **Histórico:** desde junho de 2024 (aproximadamente 2 anos)
- **Atualização:** diária via routine do Claude (ADR-004)
- **Armazenamento:** JSON estático versionado no repositório
- **Localização dos treinos:** não exibida
- **Dados excluídos:** peso corporal, comparações com outros atletas

---

## 9. Fora do Escopo

- Comparação com outros atletas ou médias externas
- Dados de peso ou composição corporal
- Gamificação (badges, troféus, streaks visuais, rankings)
- Subpáginas ou rotas (tudo em página única)
- Mapas ou localização de treinos
- Login ou área privada
- Login ou área privada (já estava fora)

---

## 10. Critérios de Sucesso

- [ ] Página carrega sem servidor (GitHub Pages estático)
- [ ] Dados atualizados automaticamente todos os dias
- [ ] KPIs exibidos com legenda explicativa em cada um
- [ ] Guardrail KPI implementado e explicado
- [ ] Plano semanal gerado e exibido pelos agentes
- [ ] Visual coerente com as referências aprovadas
- [ ] Decisões técnicas documentadas em ADRs

---

## 11. Próximos Passos

1. **ADR-001** — Arquitetura do ETL (como buscar e normalizar dados do Strava)
2. **ADR-002** — Stack da página (estrutura do HTML, bibliotecas de gráfico)
3. **ADR-003** — Schema dos dados normalizados (contrato dos JSONs)
4. **ADR-004** — Estratégia de atualização (GitHub Actions)
