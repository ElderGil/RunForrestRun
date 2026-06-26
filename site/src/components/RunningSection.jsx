// Seção Corrida: KPIs com legenda + guardrail + gráfico de evolução (PRD §4/§5).
import KPICard from "./KPICard.jsx";
import EvolutionChart from "./EvolutionChart.jsx";
import { fmtPace } from "../data/loaders.js";

export default function RunningSection({ kpis, weeks }) {
  const r = kpis.running;
  const g = r.guardrail;

  return (
    <section className="block wrap" id="corrida">
      <p className="eyebrow">Corrida</p>
      <h2>Performance e evolução</h2>
      <p className="lead">
        Cada métrica acompanha um aspecto do treino. O foco não é só velocidade —
        é evoluir sem se machucar.
      </p>

      <div className="kpi-grid">
        <KPICard value={fmtPace(r.avg_pace_min_km)} unit="min/km" label="Pace médio"
          legend="Indicador direto de velocidade e evolução de performance." />
        <KPICard value={r.longest_run_km} unit="km" label="Long run mais longo"
          legend="Preparação específica para a prova — sobe rumo aos 42 km." />
        <KPICard value={r.avg_heart_rate_bpm ?? "—"} unit="bpm" label="FC média"
          legend="Eficiência cardiovascular: menos esforço no mesmo pace = evolução real." />
        <KPICard value={r.max_heart_rate_bpm ?? "—"} unit="bpm" label="FC máxima"
          legend="Intensidade real atingida nos treinos." />
        <KPICard value={r.total_elevation_m} unit="m" label="Elevação no mês"
          legend="Força e resistência muscular em terreno variado." />
        <KPICard value={r.sessions_per_week} unit="/sem" label="Consistência"
          legend="Disciplina — o KPI mais importante a longo prazo." />
      </div>

      <div className={`guardrail ${g.status}`}>
        <div className="g-head">
          <span className="g-title">🛡️ Guardrail · {g.label}</span>
          <span>
            <span className="g-value">{g.status === "unknown" ? "—" : g.value}</span>{" "}
            <span className={`g-status ${g.status}`}>{statusLabel(g.status)}</span>
          </span>
        </div>
        <p className="g-desc">{g.description}</p>
      </div>

      <div className="chart-card">
        <div className="c-title">Volume + pace por semana</div>
        <div className="c-hint">Barras = km na semana · linha = pace médio (mais alto = mais rápido). Últimos 12 meses.</div>
        <EvolutionChart weeks={weeks} />
      </div>
    </section>
  );
}

function statusLabel(s) {
  return { ok: "saudável", warning: "atenção", danger: "risco", unknown: "sem dados" }[s] || s;
}
