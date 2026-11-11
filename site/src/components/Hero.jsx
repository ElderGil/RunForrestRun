// Resumo do mês atual (PRD §4): onde o atleta está e o que vem a seguir.
// A fase vem do plano (ADR-006); a próxima corrida, da janela de 7 dias.
import { shortDate, isoToday, lastActivity, daysSince } from "../data/loaders.js";

const WEEKDAY_LONG = { Seg: "segunda", Ter: "terça", Qua: "quarta", Qui: "quinta", Sex: "sexta", Sáb: "sábado", Dom: "domingo" };

function nextRun(plan) {
  const today = isoToday();
  for (const d of plan?.days || []) {
    if (d.date < today) continue;
    const it = (d.items || []).find((x) => x.type === "run" && !x.done);
    if (it) return { day: d, item: it };
  }
  return null;
}

export default function Hero({ kpis, plan, activities, onOpenPlan }) {
  const r = kpis.running;
  const s = kpis.strength;
  const phase = plan?.phase;
  const next = nextRun(plan);
  const lastRun = lastActivity(activities, "Run");
  const ago = lastRun ? daysSince(lastRun.date) : null;

  return (
    <header className="hero wrap">
      <p className="eyebrow">{kpis.period.label} · resumo do mês</p>
      {/* Título fixo = objetivo do projeto (ADR-006); a fase é passageira e fica num selo. */}
      <h1>
        Saúde e <span className="gradient-text">constância</span>
      </h1>
      {phase?.label && (
        <p className="phase-tag">
          Fase atual: <strong>{phase.label.toLowerCase()}</strong>
        </p>
      )}

      {next ? (
        <div className="next-up">
          <div>
            <div className="nu-label">Próxima corrida</div>
            <div className="nu-text">
              {WEEKDAY_LONG[next.day.weekday] || next.day.weekday}, {shortDate(next.day.date)} · {next.item.title}
            </div>
          </div>
          <button className="link-btn" onClick={onOpenPlan}>Ver o plano da semana</button>
        </div>
      ) : (
        <div className="next-up">
          <div className="nu-text">Foco em saúde e constância</div>
          <button className="link-btn" onClick={onOpenPlan}>Ver o plano da semana</button>
        </div>
      )}

      <div className="hero-metrics">
        <div className="metric run">
          <div className="v">{r.total_sessions}<small> {r.total_sessions === 1 ? "corrida" : "corridas"}</small></div>
          <div className="l">{r.total_distance_km} km no mês</div>
        </div>
        <div className="metric strength">
          <div className="v">{s.total_sessions}<small> {s.total_sessions === 1 ? "sessão" : "sessões"}</small></div>
          <div className="l">de força no mês</div>
        </div>
        <div className="metric">
          <div className="v">{lastRun ? shortDate(lastRun.date) : "—"}</div>
          <div className="l">
            Última corrida{ago != null ? ` · ${ago === 0 ? "hoje" : `${ago} ${ago === 1 ? "dia" : "dias"}`}` : ""}
          </div>
        </div>
      </div>
    </header>
  );
}
