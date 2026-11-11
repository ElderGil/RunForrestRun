// Gráfico de evolução: volume (km, barras) + pace (linha) no mesmo eixo X.
// Recharts ComposedChart (ADR-002). Pace em eixo invertido: mais alto = mais rápido.
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, ReferenceArea,
} from "recharts";
import { fmtPace } from "../data/loaders.js";

const BAR = "#3a6fd6";   // --blue-500
const LINE = "#0f2350";  // --blue-900
const GRID = "#e4e0da";
const TICK = "#586074";

// Ticks de pace em valores redondos, de 30 em 30 segundos.
function paceTicks(paces) {
  if (!paces.length) return { domain: [5, 7], ticks: [5, 5.5, 6, 6.5, 7] };
  const lo = Math.floor(Math.min(...paces) * 2) / 2;
  const hi = Math.ceil(Math.max(...paces) * 2) / 2;
  const ticks = [];
  for (let v = lo; v <= hi + 1e-9; v += 0.5) ticks.push(Number(v.toFixed(2)));
  return { domain: [lo, hi], ticks };
}

export default function EvolutionChart({ weeks }) {
  const data = weeks.map((w) => ({
    label: w.week_label,
    km: w.running.distance_km,
    pace: w.running.avg_pace_min_km,
  }));

  const { domain, ticks } = paceTicks(data.map((d) => d.pace).filter((p) => p != null));

  // Pausa: semanas finais sem corrida (2 ou mais) ganham uma faixa marcada.
  let lastRunIdx = -1;
  data.forEach((d, i) => { if (d.km > 0) lastRunIdx = i; });
  const pause = lastRunIdx >= 0 && data.length - 1 - lastRunIdx >= 2
    ? { x1: data[lastRunIdx + 1].label, x2: data[data.length - 1].label }
    : null;

  // Resumo em texto para leitores de tela.
  const peak = data.reduce((best, d) => (d.km > (best?.km ?? -1) ? d : best), null);
  const summary = [
    `Volume semanal de corrida nas últimas ${data.length} semanas`,
    peak ? `pico de ${peak.km} km na semana de ${peak.label}` : null,
    lastRunIdx >= 0 ? `última semana com corrida: ${data[lastRunIdx].label}` : "nenhuma corrida no período",
  ].filter(Boolean).join("; ") + ".";

  return (
    <div className="chart-wrap" role="img" aria-label={summary}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 8, bottom: 0, left: -10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: TICK }} interval="preserveStartEnd" minTickGap={24} axisLine={false} tickLine={false} />
          <YAxis yAxisId="km" tick={{ fontSize: 11, fill: TICK }} axisLine={false} tickLine={false} width={34} />
          <YAxis
            yAxisId="pace" orientation="right" reversed domain={domain} ticks={ticks} interval={0}
            tick={{ fontSize: 11, fill: TICK }} axisLine={false} tickLine={false} width={42}
            tickFormatter={(v) => fmtPace(v)}
          />
          {pause && (
            <ReferenceArea
              yAxisId="km" x1={pause.x1} x2={pause.x2} fill="#f0eeea" fillOpacity={0.9} ifOverflow="extendDomain"
              label={{ value: "pausa", position: "insideTop", fill: TICK, fontSize: 11 }}
            />
          )}
          <Tooltip
            contentStyle={{ borderRadius: 12, border: `1px solid ${GRID}`, boxShadow: "0 8px 24px rgba(19,26,44,0.1)", fontSize: 13 }}
            formatter={(value, name) => name === "Pace" ? [`${fmtPace(value)} min/km`, name] : [`${value} km`, name]}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar yAxisId="km" dataKey="km" name="Volume" fill={BAR} radius={[4, 4, 0, 0]} maxBarSize={22} />
          <Line yAxisId="pace" type="monotone" dataKey="pace" name="Pace" stroke={LINE} strokeWidth={2} dot={false} activeDot={{ r: 4 }} connectNulls />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
