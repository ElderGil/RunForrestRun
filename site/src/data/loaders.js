// Carrega os JSONs gerados pelo ETL (ADR-001) a partir de /data/.
// BASE_URL é '/' em dev e '/RunForrestRun/' em produção (GitHub Pages).

const base = import.meta.env.BASE_URL;

async function load(name) {
  const resp = await fetch(`${base}data/${name}`, { cache: "no-store" });
  if (!resp.ok) throw new Error(`Falha ao carregar ${name}: ${resp.status}`);
  return resp.json();
}

export const loadKPIs = () => load("kpis.json");
export const loadWeekly = () => load("weekly.json");
export const loadQuarterly = () => load("quarterly.json");
export const loadWeeklyPlan = () => load("weekly_plan.json");

// Pace decimal (5.42) -> "5:25 min/km"
export function fmtPace(decimal) {
  if (decimal == null) return "—";
  const totalSec = Math.round(decimal * 60);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function fmtDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" });
}

export function daysUntil(isoDate) {
  const target = new Date(isoDate + "T00:00:00");
  return Math.ceil((target - new Date()) / 86400000);
}
