// Histórico (PRD §4): 2026 em cards mensais detalhados; 2024-25 em tabela trimestral.
import { fmtPace } from "../data/loaders.js";

export default function HistorySection({ monthly, quarters, activities }) {
  const olderQuarters = [...quarters]
    .filter((q) => !q.label.endsWith("2026"))
    .reverse(); // mais recente primeiro

  const maxKm = Math.max(1, ...monthly.map((m) => m.run_km));

  // Força só existe no Strava a partir de certa data; antes disso, 0 seria enganoso.
  const firstStrength = (activities || [])
    .filter((a) => a.type === "Strength")
    .reduce((min, a) => (!min || a.date < min ? a.date : min), null);
  const showStrength = olderQuarters.some((q) => q.strength.total_sessions > 0);

  return (
    <section className="block wrap" id="historico">
      <p className="eyebrow">Histórico</p>
      <h2>A jornada em números</h2>
      <p className="lead">
        2026 mês a mês; 2024 e 2025 resumidos por trimestre. Base para os coaches e
        para enxergar a consistência ao longo do tempo.
      </p>

      <h3 className="plan-subtitle">2026 · volume mensal de corrida</h3>
      <div className="month-grid">
        {monthly.map((m) => {
          const empty = !m.run_count;
          return (
            <div className={`month-card ${empty ? "empty" : ""}`} key={m.month}>
              <div className="mc-head">
                <span className="mc-label">{m.label}</span>
                {!empty && <span className="mc-runs">{m.run_count} {m.run_count === 1 ? "corrida" : "corridas"}</span>}
              </div>
              {empty ? (
                <div className="mc-km">sem corrida</div>
              ) : (
                <>
                  <div className="mc-km">{m.run_km}<small> km</small></div>
                  <div className="mc-bar"><i style={{ width: `${(m.run_km / maxKm) * 100}%` }} /></div>
                  <div className="mc-foot">
                    <span>Long {m.longest_run_km} km</span>
                    {m.avg_pace_min_km ? <span>{fmtPace(m.avg_pace_min_km)}/km</span> : null}
                    {m.avg_heart_rate_bpm ? <span>{m.avg_heart_rate_bpm} bpm</span> : null}
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>

      {olderQuarters.length > 0 && (
        <>
          <h3 className="plan-subtitle">2024 e 2025 · por trimestre</h3>
          <div className="table-scroll">
            <table className="q-table">
              <thead>
                <tr>
                  <th>Trimestre</th>
                  <th>Corridas</th>
                  <th>Distância</th>
                  <th>Pace médio</th>
                  <th>Maior long run</th>
                  {showStrength && <th>Força</th>}
                </tr>
              </thead>
              <tbody>
                {olderQuarters.map((q) => {
                  const none = !q.running.total_sessions;
                  return (
                    <tr key={q.label}>
                      <td>{q.label}</td>
                      <td className={none ? "muted" : ""}>{q.running.total_sessions}</td>
                      <td className={none ? "muted" : ""}>{none ? "—" : `${q.running.total_distance_km} km`}</td>
                      <td className={none ? "muted" : ""}>{fmtPace(q.running.avg_pace_min_km)}</td>
                      <td className={none ? "muted" : ""}>{none ? "—" : `${q.running.longest_run_km} km`}</td>
                      {showStrength && <td>{q.strength.total_sessions}</td>}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {!showStrength && firstStrength && (
            <p className="table-note">
              Os treinos de força aparecem no Strava a partir de {firstStrength.slice(5, 7)}/{firstStrength.slice(0, 4)}.
            </p>
          )}
        </>
      )}
    </section>
  );
}
