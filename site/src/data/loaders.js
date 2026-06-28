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
export const loadMonthly = () => load("monthly.json");
export const loadActivities = () => load("activities.json");
export const loadWeeklyPlan = () => load("weekly_plan.json");
export const loadCoaches = () => load("coaches.json");

// "26/06" curto a partir de YYYY-MM-DD
export function shortDate(iso) {
  if (!iso) return "";
  const [, m, d] = iso.split("-");
  return `${d}/${m}`;
}

// ISO local "YYYY-MM-DD" de hoje (sem deslocamento de fuso).
export function isoToday() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// Rótulo curto do dia da semana em pt-BR, capitalizado e sem ponto: "Seg", "Dom".
export function weekdayShort(iso) {
  if (!iso) return "";
  const d = new Date(iso + "T12:00:00");
  const s = d.toLocaleDateString("pt-BR", { weekday: "short" }).replace(".", "");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Data (dd/mm) de um dia da semana a partir da segunda-feira (week_of) + índice.
export function dayDate(weekOf, index) {
  const d = new Date(weekOf + "T12:00:00");
  d.setDate(d.getDate() + index);
  return `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}`;
}

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
  // Datas sem hora (YYYY-MM-DD) são fixadas ao meio-dia para evitar
  // que o fuso horário empurre para o dia anterior.
  const d = iso.length === 10 ? new Date(iso + "T12:00:00") : new Date(iso);
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" });
}

export function daysUntil(isoDate) {
  const target = new Date(isoDate + "T00:00:00");
  return Math.ceil((target - new Date()) / 86400000);
}
