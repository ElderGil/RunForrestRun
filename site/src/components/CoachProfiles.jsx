// Resumo do perfil de cada skill (running-coach / strength-coach) + dados do atleta.
export default function CoachProfiles({ coaches }) {
  if (!coaches) return null;
  const a = coaches.athlete;

  return (
    <div className="coaches">
      <p className="eyebrow">Os coaches</p>
      <h2>Quem monta o plano</h2>
      <p className="lead">
        Dois agentes analisam os dados e o histórico do atleta para montar a semana.
      </p>

      {a && (
        <div className="athlete-card">
          <span className="athlete-facts">
            <strong>{a.age} anos</strong> · <strong>{a.weight_kg} kg</strong>
          </span>
          <span className="athlete-note">{a.notes}</span>
        </div>
      )}

      <div className="coach-grid">
        {coaches.coaches.map((c) => (
          <div className="coach-card" key={c.id}>
            <div className="coach-head">
              <span className="coach-emoji">{c.emoji}</span>
              <div>
                <div className="coach-name">{c.name}</div>
                <div className="coach-role">{c.role}</div>
              </div>
            </div>
            <p className="coach-summary">{c.summary}</p>
            <ul className="coach-focus">
              {c.focus.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
