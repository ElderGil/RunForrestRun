// Perfil dos coaches: quem são, versão, resumo e principais configurações do agent.
export default function CoachProfiles({ coaches }) {
  if (!coaches) return null;

  return (
    <div className="coaches">
      <p className="eyebrow">Seus coaches</p>
      <h2>Um sistema de coach de corrida e força</h2>
      <p className="lead">
        Dois agentes que leem seus treinos do Strava e se adaptam ao que você
        realmente faz. Abaixo, o perfil de cada um; mais adiante, o plano da semana.
      </p>

      <div className="coach-grid">
        {coaches.coaches.map((c) => (
          <div className="coach-card" key={c.id}>
            <div className="coach-head">
              <span className="coach-emoji">{c.emoji}</span>
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
