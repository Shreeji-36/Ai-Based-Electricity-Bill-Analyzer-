"use client";
import type { ReactNode } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { Result } from "@/lib/api";

const COLORS = ["#14b8a6", "#38bdf8", "#a78bfa", "#f59e0b", "#f472b6", "#34d399", "#94a3b8"];
const tip = {
  contentStyle: { background: "#0f172a", border: "1px solid #334155", borderRadius: 12 },
  labelStyle: { color: "#e2e8f0" },
};
const axis = { stroke: "#64748b", fontSize: 12 };
const short = (s: string) => (s.length > 18 ? s.slice(0, 17) + "…" : s);

function Box({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="card">
      <h3 className="mb-3 font-semibold">{title}</h3>
      <div className="h-72">{children}</div>
    </div>
  );
}

export function SharePie({ rows }: { rows: Result["rows"] }) {
  return (
    <Box title="Consumption share by machine">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={rows} dataKey="units" nameKey="name" innerRadius={55} outerRadius={95} paddingAngle={2}>
            {rows.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip {...tip} formatter={(v) => `${Number(v).toLocaleString("en-IN")} kWh`} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
}

function HBar({ title, data, unit, color }: {
  title: string; data: { name: string; value: number }[]; unit: string; color: string;
}) {
  return (
    <Box title={title}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
          <CartesianGrid stroke="#1e293b" horizontal={false} />
          <XAxis type="number" {...axis} />
          <YAxis type="category" dataKey="name" width={130} tickFormatter={short} {...axis} />
          <Tooltip {...tip} formatter={(v) => `${Number(v).toLocaleString("en-IN")} ${unit}`} />
          <Bar dataKey="value" fill={color} radius={[0, 6, 6, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}

export const CostBar = ({ r }: { r: Result }) => (
  <HBar title="Electricity cost per machine" unit="₹" color="#14b8a6"
    data={r.rows.map((x) => ({ name: x.name, value: x.cost }))} />
);

export const DailyBar = ({ r }: { r: Result }) => (
  <HBar title="Average daily consumption (kWh/day)" unit="kWh/day" color="#38bdf8"
    data={r.rows.map((x) => ({ name: x.name, value: Math.round(x.units / (r.bill.days || 30)) }))} />
);

export const EfficiencyBar = ({ r }: { r: Result }) => (
  <HBar title="Machine efficiency comparison (%)" unit="%" color="#a78bfa"
    data={r.rows.filter((x) => x.name !== "Others").map((x) => ({ name: x.name, value: x.efficiency }))} />
);

export function TrendLine({ r }: { r: Result }) {
  const f = r.ai.forecast;
  const data = [
    { m: "Current", units: r.bill.units, low: r.bill.units, high: r.bill.units },
    ...f.units.map((u, i) => ({ m: `+${i + 1} mo`, units: u, low: f.low[i], high: f.high[i] })),
  ];
  return (
    <Box title="Monthly trend and forecast (kWh)">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ left: 8, right: 16 }}>
          <CartesianGrid stroke="#1e293b" />
          <XAxis dataKey="m" {...axis} />
          <YAxis {...axis} />
          <Tooltip {...tip} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line dataKey="units" name="Forecast" stroke="#14b8a6" strokeWidth={3} dot />
          <Line dataKey="high" name="High" stroke="#f59e0b" strokeDasharray="5 5" dot={false} />
          <Line dataKey="low" name="Low" stroke="#38bdf8" strokeDasharray="5 5" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}