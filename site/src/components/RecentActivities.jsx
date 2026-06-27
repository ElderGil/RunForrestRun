// Últimas atividades — contexto além dos números do mês (PRD §4).
import { shortDate, fmtPace } from "../data/loaders.js";

const TYPE_META = {
  Run: { icon: "🏃", cls: "run" },
  Strength: { icon: "🏋️", cls: "strength" },
  Ride: { icon: "🚴", cls: "ride" },
};

export default function RecentActivities({ activities }) {
  if (!activities?.length) return null;
  const recent = [...activities].reverse().slice(0, 6);

  return (
    <section className="block wrap">
      <p className="eyebrow">Últimas atividades</p>
      <h2>O que rolou por aqui</h2>
      <p className="lead">As sessões mais recentes — não só o número, o treino.</p>

      <ul className="act-list">
        {recent.map((a) => {
          const m = TYPE_META[a.type] || { icon: "•", cls: "" };
          return (
            <li className={`act ${m.cls}`} key={a.id}>
              <span className="act-icon">{m.icon}</span>
              <span className="act-main">
                <span className="act-name">{a.name}</span>
                <span className="act-date">{shortDate(a.date)}</span>
              </span>
              <span className="act-stats">
                {a.type === "Run" ? (
                  <>
                    <b>{a.distance_km} km</b>
                    <span>{fmtPace(a.pace_min_km)}/km</span>
                    {a.avg_heart_rate_bpm ? <span>{a.avg_heart_rate_bpm} bpm</span> : null}
                  </>
                ) : (
                  <>
                    <b>{Math.round(a.duration_min)} min</b>
                    {a.avg_heart_rate_bpm ? <span>{a.avg_heart_rate_bpm} bpm</span> : null}
                  </>
                )}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
