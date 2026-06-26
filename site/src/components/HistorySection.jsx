// Seção Histórico: visão agregada por quarter desde jun/2024 (PRD §4).
import { fmtPace } from "../data/loaders.js";

export default function HistorySection({ quarters }) {
  const rows = [...quarters].reverse(); // mais recente primeiro

  return (
    <section className="block wrap" id="historico">
      <p className="eyebrow">Histórico</p>
      <h2>A jornada por trimestre</h2>
      <p className="lead">
        Visão macro desde junho de 2024. Referência para os coaches e para enxergar a
        consistência ao longo do tempo.
      </p>

      <table className="q-table">
        <thead>
          <tr>
            <th>Trimestre</th>
            <th>Corridas</th>
            <th>Distância</th>
            <th>Pace médio</th>
            <th>Maior long run</th>
            <th>Força</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((q) => (
            <tr key={q.label}>
              <td>{q.label}</td>
              <td>{q.running.total_sessions}</td>
              <td>{q.running.total_distance_km} km</td>
              <td>{fmtPace(q.running.avg_pace_min_km)}</td>
              <td>{q.running.longest_run_km} km</td>
              <td>{q.strength.total_sessions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
