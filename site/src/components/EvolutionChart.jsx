// Gráfico de evolução: volume (km, barras) + pace (linha) no mesmo eixo X.
// Recharts ComposedChart (ADR-002). Pace em eixo invertido — mais alto = mais rápido.
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import { fmtPace } from "../data/loaders.js";

export default function EvolutionChart({ weeks }) {
  const data = weeks.map((w) => ({
    label: w.week_label,
    km: w.running.distance_km,
    pace: w.running.avg_pace_min_km,
  }));

  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 8, bottom: 0, left: -10 }}>
          <defs>
            <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a855f7" stopOpacity={0.95} />
              <stop offset="100%" stopColor="#fb923c" stopOpacity={0.7} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#ece8f0" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#6b6577" }} interval="preserveStartEnd" minTickGap={24} axisLine={false} tickLine={false} />
          <YAxis yAxisId="km" tick={{ fontSize: 11, fill: "#6b6577" }} axisLine={false} tickLine={false} width={34} />
          <YAxis
            yAxisId="pace" orientation="right" reversed domain={["dataMin - 0.3", "dataMax + 0.3"]}
            tick={{ fontSize: 11, fill: "#6b6577" }} axisLine={false} tickLine={false} width={42}
            tickFormatter={(v) => fmtPace(v)}
          />
          <Tooltip
            contentStyle={{ borderRadius: 12, border: "1px solid #ece8f0", boxShadow: "0 8px 24px rgba(26,23,38,0.1)", fontSize: 13 }}
            formatter={(value, name) => name === "Pace" ? [`${fmtPace(value)} min/km`, name] : [`${value} km`, name]}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar yAxisId="km" dataKey="km" name="Volume" fill="url(#barGrad)" radius={[4, 4, 0, 0]} maxBarSize={22} />
          <Line yAxisId="pace" type="monotone" dataKey="pace" name="Pace" stroke="#7c3aed" strokeWidth={2.5} dot={false} connectNulls />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
