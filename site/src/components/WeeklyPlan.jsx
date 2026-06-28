// Caixa "Coach": análise + indicadores + plano rolante de 7 dias (hoje + 6).
// Schema 3.0 (ADR-005): janela móvel com datas reais; destaca hoje e amanhã.
import { fmtDate, shortDate, isoToday, weekdayShort } from "../data/loaders.js";

function nextDayIso(iso) {
  const d = new Date(iso + "T12:00:00");
  d.setDate(d.getDate() + 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export default function WeeklyPlan({ plan }) {
  if (!plan) {
    return (
      <div className="week-coach">
        <p className="eyebrow">Coach</p>
        <h2>Plano sendo gerado</h2>
        <p className="lead">
          O coach ainda não publicou a análise. Aparece aqui assim que a próxima
          atualização do Strava rodar.
        </p>
      </div>
    );
  }

  const c = plan.coaches || {};
  const today = isoToday();
  const tomorrow = nextDayIso(today);
  const days = plan.days || [];

  const rangeLabel = plan.window_start
    ? `${shortDate(plan.window_start)} – ${shortDate(plan.window_end)}`
    : plan.week_label || fmtDate(plan.week_of);

  return (
    <div className="week-coach">
      <p className="eyebrow">Coach · próximos 7 dias · {rangeLabel}</p>
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

      <h3 className="plan-subtitle">Plano · próximos 7 dias</h3>
      <div className="plan-grid">
        {days.map((d, i) => {
          const date = d.date || null;
          const isToday = date === today;
          const isTomorrow = date === tomorrow;
          const wd = d.weekday || (date ? weekdayShort(date) : d.day) || "";
          const items = d.items || [];
          return (
            <div
              className={`day ${isToday ? "today" : ""} ${isTomorrow ? "tomorrow" : ""}`}
              key={date || i}
            >
              <div className="d-name">
                {wd} {date && <span className="d-date">{shortDate(date)}</span>}
                {isToday && <span className="d-tag">hoje</span>}
                {isTomorrow && <span className="d-tag soft">amanhã</span>}
              </div>
              {items.length === 0 ? (
                <div className="chip rest">Livre</div>
              ) : (
                items.map((it, idx) => (
                  <div className={`chip ${it.type} ${it.done ? "done" : ""}`} key={idx}>
                    {it.done ? "✓ " : ""}{it.title}
                    {it.detail ? <span className="c-detail">{it.detail}</span> : null}
                  </div>
                ))
              )}
            </div>
          );
        })}
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
