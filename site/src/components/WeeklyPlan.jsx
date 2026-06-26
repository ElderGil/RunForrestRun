// Aba Plano Semanal (PRD §4 / §7): calendário unificado corrida + força + descanso,
// gerado pelos agentes running-coach e strength-coach. Adapta quando treinos não são
// executados conforme planejado.
import { fmtDate, dayDate } from "../data/loaders.js";
import CoachProfiles from "./CoachProfiles.jsx";

export default function WeeklyPlan({ plan, coaches }) {
  if (!plan) {
    return (
      <section className="block wrap">
        <CoachProfiles coaches={coaches} />
        <p className="eyebrow">Plano semanal</p>
        <h2>Plano sendo gerado</h2>
        <p className="lead">
          Os coaches ainda não publicaram o plano desta semana. Ele aparece aqui assim
          que running-coach e strength-coach rodarem sobre os dados mais recentes.
        </p>
      </section>
    );
  }

  return (
    <section className="block wrap">
      <CoachProfiles coaches={coaches} />

      <p className="eyebrow">Plano semanal · semana de {fmtDate(plan.week_of)}</p>
      <h2>Calendário de treinos</h2>
      <p className="lead">{plan.summary}</p>

      <div className="plan-grid">
        {plan.days.map((d, i) => (
          <div className="day" key={d.day}>
            <div className="d-name">{d.day} <span className="d-date">{dayDate(plan.week_of, i)}</span></div>
            {d.items.length === 0 ? (
              <div className="chip rest">Livre</div>
            ) : (
              d.items.map((it, i) => (
                <div className={`chip ${it.type}`} key={i}>
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

      {(plan.coaches?.running || plan.coaches?.strength) && (
        <div className="chart-card" style={{ marginTop: "1.5rem" }}>
          {plan.coaches.running && (
            <p className="g-desc" style={{ marginTop: 0 }}>
              <strong>🏃 running-coach:</strong> {plan.coaches.running}
            </p>
          )}
          {plan.coaches.strength && (
            <p className="g-desc">
              <strong>🏋️ strength-coach:</strong> {plan.coaches.strength}
            </p>
          )}
        </div>
      )}

      <p className="plan-note">
        O plano é gerado semanalmente pelos agentes e se ajusta automaticamente quando
        um treino não é executado conforme o planejado.
      </p>
    </section>
  );
}
