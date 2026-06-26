// Caixa "Coach da semana": análise + indicadores + plano que se adapta ao que foi feito.
import { fmtDate, dayDate } from "../data/loaders.js";

export default function WeeklyPlan({ plan }) {
  if (!plan) {
    return (
      <div className="week-coach">
        <p className="eyebrow">Coach da semana</p>
        <h2>Plano sendo gerado</h2>
        <p className="lead">
          O coach ainda não publicou a análise desta semana. Aparece aqui assim que
          a próxima atualização do Strava rodar.
        </p>
      </div>
    );
  }

  const c = plan.coaches || {};

  return (
    <div className="week-coach">
      <p className="eyebrow">Coach da semana · {plan.week_label || fmtDate(plan.week_of)}</p>
      <h2>O que o coach diz</h2>
      <p className="lead">{plan.summary}</p>

      {plan.indicators?.length > 0 && (
        <div className="indicators">
          {plan.indicators.map((ind, i) => (
            <div className={`indicator ${ind.status || ""}`} key={i}>
              <div className="ind-value">{ind.value}</div>
              <div className="ind-label">{ind.label}</div>
            </div>
          ))}
        </div>
      )}

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

      {plan.adaptations?.length > 0 && (
        <div className="adaptations">
          <div className="adapt-title">🔄 Como o coach se adaptou</div>
          <ul>
            {plan.adaptations.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </div>
      )}

      <h3 className="plan-subtitle">Plano da semana</h3>
      <div className="plan-grid">
        {plan.days.map((d, i) => (
          <div className="day" key={d.day}>
            <div className="d-name">{d.day} <span className="d-date">{dayDate(plan.week_of, i)}</span></div>
            {d.items.length === 0 ? (
              <div className="chip rest">Livre</div>
            ) : (
              d.items.map((it, idx) => (
                <div className={`chip ${it.type} ${it.done ? "done" : ""}`} key={idx}>
                  {it.done ? "✓ " : ""}{it.title}
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
        <span><i style={{ background: "#dcfce7" }} /> ✓ Feito</span>
      </div>
    </div>
  );
}
