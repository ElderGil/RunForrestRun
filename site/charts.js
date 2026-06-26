// RunForrestRun — carrega dados normalizados e renderiza os gráficos.

const COLORS = {
  accent: "#fc4c02",
  accentSoft: "#ff7a40",
  green: "#3fb950",
  blue: "#58a6ff",
  purple: "#bc8cff",
  dim: "#8b98a5",
  grid: "rgba(138, 152, 165, 0.12)",
};

// data/ fica na raiz do repo; o site pode ser servido da raiz (GitHub Pages)
// ou de dentro de site/ (local). Tentamos ambos os caminhos.
async function loadJSON(name) {
  for (const base of ["../data/", "data/", "./data/"]) {
    try {
      const resp = await fetch(base + name, { cache: "no-store" });
      if (resp.ok) return await resp.json();
    } catch (_) { /* tenta o próximo */ }
  }
  throw new Error("Não foi possível carregar " + name);
}

function fmtDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
}

// ---- Countdown ----
function renderCountdowns() {
  const now = new Date();
  document.querySelectorAll(".goal-countdown").forEach((el) => {
    const target = new Date(el.dataset.target + "T00:00:00");
    const days = Math.ceil((target - now) / 86400000);
    el.textContent = days > 0 ? `${days} dias` : "chegou! 🎉";
  });
}

// ---- KPIs ----
function renderKPIs(kpis) {
  const items = [
    { value: kpis.avg_pace_str, unit: "min/km", label: "Pace médio (últimas 5)" },
    { value: kpis.avg_weekly_run_km, unit: "km", label: "Média semanal (4 sem)" },
    { value: kpis.long_run_km, unit: "km", label: "Maior long run" },
    { value: kpis.consistency_pct_12w, unit: "%", label: "Consistência (12 sem)" },
    { value: kpis.total_run_km, unit: "km", label: "Total corrido" },
    { value: kpis.total_run_count, unit: "", label: "Corridas registradas" },
  ];
  const el = document.getElementById("kpis");
  el.innerHTML = items.map((i) => `
    <div class="kpi">
      <div class="kpi-value">${i.value}${i.unit ? ` <small>${i.unit}</small>` : ""}</div>
      <div class="kpi-label">${i.label}</div>
    </div>`).join("");
}

// ---- Chart defaults ----
function baseOptions(extra = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: COLORS.dim, font: { size: 12 } } },
      tooltip: { mode: "index", intersect: false },
    },
    scales: {
      x: { ticks: { color: COLORS.dim, maxRotation: 0, autoSkip: true, maxTicksLimit: 12 }, grid: { color: COLORS.grid } },
      y: { ticks: { color: COLORS.dim }, grid: { color: COLORS.grid }, beginAtZero: true },
    },
    ...extra,
  };
}

function gradient(ctx, color) {
  const g = ctx.createLinearGradient(0, 0, 0, 300);
  g.addColorStop(0, color + "66");
  g.addColorStop(1, color + "08");
  return g;
}

async function main() {
  Chart.defaults.color = COLORS.dim;
  Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;

  renderCountdowns();

  const [kpis, weekly, monthly] = await Promise.all([
    loadJSON("kpis.json"),
    loadJSON("weekly.json"),
    loadJSON("monthly.json"),
  ]);

  document.getElementById("updated").textContent =
    "Dados atualizados em " + fmtDate(kpis.as_of);

  renderKPIs(kpis);

  // Limita ao último ano para legibilidade (52 semanas)
  const recentWeeks = weekly.slice(-52);
  const weekLabels = recentWeeks.map((w) => w.week.replace(/^\d{4}-W/, "S"));

  // Volume semanal de corrida
  new Chart(document.getElementById("weeklyChart"), {
    type: "bar",
    data: {
      labels: weekLabels,
      datasets: [{
        label: "km corridos",
        data: recentWeeks.map((w) => w.run_km),
        backgroundColor: COLORS.accent,
        borderRadius: 4,
      }],
    },
    options: baseOptions(),
  });

  // Evolução do pace (apenas semanas com corrida)
  const paceWeeks = recentWeeks.filter((w) => w.avg_pace_s_per_km);
  new Chart(document.getElementById("paceChart"), {
    type: "line",
    data: {
      labels: paceWeeks.map((w) => w.week.replace(/^\d{4}-W/, "S")),
      datasets: [{
        label: "pace médio (s/km)",
        data: paceWeeks.map((w) => w.avg_pace_s_per_km),
        borderColor: COLORS.blue,
        backgroundColor: (c) => gradient(c.chart.ctx, COLORS.blue),
        fill: true,
        tension: 0.3,
        pointRadius: 2,
      }],
    },
    options: baseOptions({
      scales: {
        x: { ticks: { color: COLORS.dim, maxTicksLimit: 12 }, grid: { color: COLORS.grid } },
        y: {
          reverse: true, // menor pace (mais rápido) no topo
          ticks: {
            color: COLORS.dim,
            callback: (v) => `${Math.floor(v / 60)}:${String(Math.round(v % 60)).padStart(2, "0")}`,
          },
          grid: { color: COLORS.grid },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (c) => `${Math.floor(c.parsed.y / 60)}:${String(Math.round(c.parsed.y % 60)).padStart(2, "0")} min/km`,
          },
        },
      },
    }),
  });

  // Volume mensal por modalidade
  const monthLabels = monthly.map((m) => m.month);
  new Chart(document.getElementById("monthlyChart"), {
    type: "bar",
    data: {
      labels: monthLabels,
      datasets: [
        { label: "Corrida", data: monthly.map((m) => m.run_km), backgroundColor: COLORS.accent, borderRadius: 3, stack: "km" },
        { label: "Bike", data: monthly.map((m) => m.ride_km), backgroundColor: COLORS.blue, borderRadius: 3, stack: "km" },
      ],
    },
    options: baseOptions({
      scales: {
        x: { stacked: true, ticks: { color: COLORS.dim, maxTicksLimit: 12 }, grid: { color: COLORS.grid } },
        y: { stacked: true, beginAtZero: true, ticks: { color: COLORS.dim }, grid: { color: COLORS.grid } },
      },
    }),
  });

  // Long run por mês
  new Chart(document.getElementById("longRunChart"), {
    type: "line",
    data: {
      labels: monthLabels,
      datasets: [{
        label: "long run (km)",
        data: monthly.map((m) => m.long_run_km),
        borderColor: COLORS.green,
        backgroundColor: (c) => gradient(c.chart.ctx, COLORS.green),
        fill: true,
        tension: 0.3,
        pointRadius: 3,
      }],
    },
    options: baseOptions({ plugins: { legend: { display: false } } }),
  });

  // Força por semana
  new Chart(document.getElementById("strengthChart"), {
    type: "bar",
    data: {
      labels: weekLabels,
      datasets: [{
        label: "treinos de força",
        data: recentWeeks.map((w) => w.strength_count),
        backgroundColor: COLORS.purple,
        borderRadius: 4,
      }],
    },
    options: baseOptions({ plugins: { legend: { display: false } } }),
  });
}

main().catch((err) => {
  console.error(err);
  document.getElementById("updated").textContent = "Erro ao carregar os dados.";
});
