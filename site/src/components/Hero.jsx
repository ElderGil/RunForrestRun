// Resumo do mês atual (PRD §4): contexto antes dos números.
// A frase de objetivo vem da fase do plano (ADR-006), não de uma data de prova fixa.
import { fmtPace } from "../data/loaders.js";

export default function Hero({ kpis, plan }) {
  const r = kpis.running;
  const phase = plan?.phase;

  return (
    <header className="hero wrap">
      <p className="eyebrow">{kpis.period.label} · resumo do mês</p>
      <h1>
        Running <span className="gradient-text">Coach</span>
      </h1>

      <span className="goal-line">
        <span className="goal-dot" />
        {phase ? (
          <span>
            <strong>{phase.label}</strong>
            {phase.detail ? ` · ${phase.detail}` : null}
          </span>
        ) : (
          <span>Foco em saúde e constância</span>
        )}
      </span>

      <div className="hero-metrics">
        <div className="metric">
          <div className="v">{r.total_distance_km}<small> km</small></div>
          <div className="l">Corridos no mês</div>
        </div>
        <div className="metric">
          <div className="v">{r.total_sessions}</div>
          <div className="l">Treinos de corrida</div>
        </div>
        <div className="metric">
          <div className="v">{fmtPace(r.avg_pace_min_km)}<small> /km</small></div>
          <div className="l">Pace médio</div>
        </div>
      </div>
    </header>
  );
}
