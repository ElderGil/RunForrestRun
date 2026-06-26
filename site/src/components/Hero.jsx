// Resumo do mês atual (PRD §4): contexto antes dos números.
import { fmtPace, daysUntil } from "../data/loaders.js";

export default function Hero({ kpis }) {
  const r = kpis.running;
  const daysToHalf = daysUntil("2026-10-17");

  return (
    <header className="hero wrap">
      <p className="eyebrow">{kpis.period.label} · resumo do mês</p>
      <h1>
        1% melhor <span className="gradient-text">toda semana</span>,<br />
        rumo à maratona.
      </h1>
      <p className="sub">
        Documentando uma jornada real de treinamento com dados do Strava — do jeito
        que um engenheiro documenta um projeto de software. Tudo visível, tudo explicado.
      </p>

      <span className="goal-line">
        <span className="goal-dot" />
        Faltam <strong>&nbsp;{daysToHalf} dias&nbsp;</strong> para a meia maratona de Pomerode
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
