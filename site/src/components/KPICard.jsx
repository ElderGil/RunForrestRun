// Card reutilizável de KPI com legenda explicativa (PRD §5).
export default function KPICard({ value, unit, label, legend }) {
  return (
    <div className="kpi">
      <div className="k-value">
        {value}
        {unit ? <small> {unit}</small> : null}
      </div>
      <div className="k-label">{label}</div>
      {legend ? <div className="k-legend">{legend}</div> : null}
    </div>
  );
}
