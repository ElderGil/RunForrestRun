// Caixa "Coach": análise + indicadores + plano rolante de 7 dias (hoje + 6).
// Schema 3.0 (ADR-005): janela móvel com datas reais; destaca hoje e amanhã.
import { fmtDate, shortDate, isoToday, weekdayShort } from "../data/loaders.js";
import { RunIcon, StrengthIcon, RefreshIcon } from "./Icons.jsx";

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

  // A routine roda por volta das 11h, então de manhã a janela ainda começa ontem.
  // Dois dias ou mais de atraso = a atualização diária parou.
  const lagDays = plan.window_start
    ? Math.round((new Date(today + "T12:00:00") - new Date(plan.window_start + "T12:00:00")) / 86400000)
    : 0;
  const stale = lagDays >= 2;

  const rangeLabel = plan.window_start
    ? `${shortDate(plan.window_start)} – ${shortDate(plan.window_end)}`
    : plan.week_label || fmtDate(plan.week_of);

  return (
    <div className="week-coach">
      <p className="eyebrow">Coach · próximos 7 dias · {rangeLabel}</p>
      <h2>O plano da semana</h2>
      {stale && (
        <p className="stale-notice" role="status">
          Plano desatualizado: foi gerado em {fmtDate(plan.window_start)}, {lagDays} dias atrás.
          A atualização diária não rodou desde então, então os dias abaixo podem não valer mais.
        </p>
      )}
      <p className="lead">{plan.summary}</p>

      <ol className="plan-grid">
        {days.map((d, i) => {
          const date = d.date || null;
          const isToday = date === today;
          const isTomorrow = date === tomorrow;
          const wd = d.weekday || (date ? weekdayShort(date) : d.day) || "";
          const items = d.items || [];
          return (
            <li
              className={`day ${isToday ? "today" : ""} ${isTomorrow ? "tomorrow" : ""}`}
              key={date || i}
              aria-current={isToday ? "date" : undefined}
            >
              <div className="d-name">
                {wd} {date && <span className="d-date">{shortDate(date)}</span>}
                {isToday && <span className="d-tag">hoje</span>}
                {isTomorrow && <span className="d-tag soft">amanhã</span>}
              </div>
              <div className="d-items">
                {items.length === 0 ? (
                  <div className="chip rest">Dia livre</div>
                ) : (
                  items.map((it, idx) => (
                    <div className={`chip ${it.type}`} key={idx}>
                      {it.done ? <span className="c-done">Feito</span> : null}
                      {it.title}
                      {it.detail ? <span className="c-detail">{it.detail}</span> : null}
                    </div>
                  ))
                )}
              </div>
            </li>
          );
        })}
      </ol>

      <div className="legend" aria-hidden="true">
        <span><i style={{ background: "var(--run)" }} /> Corrida</span>
        <span><i style={{ background: "var(--strength)" }} /> Força</span>
        <span><i style={{ background: "#b9b4ab" }} /> Dia livre</span>
        <span><em className="c-done">Feito</em> já registrado no Strava</span>
      </div>

      {plan.indicators?.length > 0 && (
        <>
          <h3 className="plan-subtitle">Indicadores</h3>
          <div className="indicators">
            {plan.indicators.map((ind, i) => {
              // Planos antigos trazem a frase inteira em `value`; sem `detail`, ela vira texto normal.
              const long = !ind.detail && ind.value.length > 32;
              return (
                <div className={`indicator ${ind.status || "unknown"}`} key={i}>
                  <div className="ind-head">
                    <span className="ind-label">{ind.label}</span>
                    <span className={`g-status ${ind.status || "unknown"}`}>{STATUS_LABEL[ind.status] || "sem dados"}</span>
                  </div>
                  <div className={`ind-value ${long ? "long" : ""}`}>{ind.value}</div>
                  {ind.detail ? <div className="ind-detail">{ind.detail}</div> : null}
                </div>
              );
            })}
          </div>
        </>
      )}

      {(c.running || c.strength) && (
        <>
          <h3 className="plan-subtitle">O que os coaches dizem</h3>
          <div className="coach-notes">
            {c.running && (
              <div className="coach-note run">
                <div className="cn-head"><RunIcon /> Running Coach</div>
                <p>{c.running}</p>
              </div>
            )}
            {c.strength && (
              <div className="coach-note strength">
                <div className="cn-head"><StrengthIcon /> Strength Coach</div>
                <p>{c.strength}</p>
              </div>
            )}
          </div>
        </>
      )}

      {plan.adaptations?.length > 0 && (
        <details className="adaptations">
          <summary>
            <RefreshIcon width={18} height={18} aria-hidden="true" /> Como o coach se adaptou
            <span className="adapt-count">({plan.adaptations.length})</span>
          </summary>
          <ul>
            {plan.adaptations.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </details>
      )}
    </div>
  );
}

const STATUS_LABEL = { ok: "saudável", warning: "atenção", danger: "risco", unknown: "sem dados" };
