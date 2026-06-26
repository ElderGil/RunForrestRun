// Aba Plano Semanal: a leitura do coach sobre o treino + o plano da semana (com datas).
import { fmtDate, dayDate } from "../data/loaders.js";

export default function WeeklyPlan({ plan }) {
  if (!plan) {
    return (
      <section className="block wrap">
        <p className="eyebrow">Coach</p>
        <h2>Plano sendo gerado</h2>
        <p className="lead">
          O coach ainda não publicou a análise e o plano desta semana. Aparece aqui
          assim que rodar sobre os treinos mais recentes.
        </p>
      </section>
    );
  }

  const c = plan.coaches || {};

  return (
    <section className="block wrap">
      <p className="eyebrow">Coach · semana de {fmtDate(plan.week_of)}</p>
      <h2>A leitura do coach</h2>

      {(c.running || c.strength) && (
        <div className="coach-notes">
          {c.running && (
            <div className="coach-note run">
              <div className="cn-head"><span>🏃</span> Running Coach</div>
              <p>{c.running}</p>
            </div>
          )}
          {c.strength && (
            <div className="coach-note strength">
              <div className="cn-head"><span>🏋️</span> Strength Coach</div>
              <p>{c.strength}</p>
            </div>
          )}
        </div>
      )}

      <h3 className="plan-subtitle">Plano da semana</h3>
      <p className="lead">{plan.summary}</p>

      <div className="plan-grid">
        {plan.days.map((d, i) => (
          <div className="day" key={d.day}>
            <div className="d-name">{d.day} <span className="d-date">{dayDate(plan.week_of, i)}</span></div>
            {d.items.length === 0 ? (
              <div className="chip rest">Livre</div>
            ) : (
              d.items.map((it, idx) => (
                <div className={`chip ${it.type}`} key={idx}>
                  {it.title}
                  {it.detail ? <span className="c-detail">{it.detail}</span> : null}
                </div>
              ))
            )}
          </div>
        ))}
      </div>

      <div className="legend">
        <span><i style={{ background: "linear-gradient(135deg,#e0f2fe,#dbeafe)" }} /> Corrida</span>
        <span><i style={{ background: "#fff1e6" }} /> Força</span>
        <span><i style={{ background: "#f1f5f9" }} /> Descanso</span>
      </div>
    </section>
  );
}
