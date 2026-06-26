// Seção Força: KPIs de treino complementar (PRD §4/§5).
import KPICard from "./KPICard.jsx";

export default function StrengthSection({ kpis }) {
  const s = kpis.strength;
  const focusLabel = { lower_body: "Trem inferior", upper_body: "Trem superior", full_body: "Corpo todo" }[s.focus] || s.focus;

  return (
    <section className="block wrap" id="forca">
      <p className="eyebrow">Força</p>
      <h2>O suporte da corrida</h2>
      <p className="lead">
        Musculação com foco em pernas sustenta o volume de corrida e reduz risco de lesão.
        Força e corrida como sistema — não competindo.
      </p>

      <div className="kpi-grid">
        <KPICard value={s.total_sessions} label="Sessões no mês"
          legend="Consistência do treino complementar à corrida." />
        <KPICard value={s.sessions_per_week} unit="/sem" label="Frequência semanal"
          legend="Equilíbrio entre estímulo e recuperação." />
        <KPICard value={focusLabel} label="Foco atual"
          legend="Grupo muscular priorizado na fase atual do ciclo." />
      </div>
    </section>
  );
}
