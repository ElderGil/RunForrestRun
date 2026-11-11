// Perfil dos coaches: quem são, versão, resumo e principais configurações do agent.
import { RunIcon, StrengthIcon } from "./Icons.jsx";

export default function CoachProfiles({ coaches }) {
  if (!coaches) return null;

  return (
    <div className="coaches">
      <p className="eyebrow">Quem monta o plano</p>
      <h2>Dois coaches, um plano</h2>
      <p className="lead">
        Dois agentes leem os treinos do Strava todo dia e ajustam o plano acima ao que
        foi feito de verdade. Este é o perfil de cada um.
      </p>

      <div className="coach-grid">
        {coaches.coaches.map((c) => (
          <div className="coach-card" key={c.id}>
            <div className="coach-head">
              <span className={`coach-icon ${c.id === "strength-coach" ? "strength" : ""}`}>
                {c.id === "strength-coach" ? <StrengthIcon width={22} height={22} /> : <RunIcon width={22} height={22} />}
              </span>
              <div>
                <div className="coach-name">
                  {c.name} <span className="coach-version">v{c.version}</span>
                </div>
                <div className="coach-role">{c.tagline}</div>
              </div>
            </div>
            <p className="coach-summary">{c.summary}</p>
            <dl className="coach-config">
              {c.config.map((cfg, i) => (
                <div className="cfg-row" key={i}>
                  <dt>{cfg.label}</dt>
                  <dd>{cfg.value}</dd>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </div>
    </div>
  );
}
