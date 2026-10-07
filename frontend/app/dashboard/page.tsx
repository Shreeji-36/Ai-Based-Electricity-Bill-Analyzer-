"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { CostBar, DailyBar, EfficiencyBar, SharePie, TrendLine } from "@/components/Charts";
import { downloadReport, type Payload, type Result } from "@/lib/api";

const inr = (n: number) => "₹" + Math.round(n).toLocaleString("en-IN");
const num = (n: number) => Math.round(n).toLocaleString("en-IN");

type Saved = { payload: Payload; result: Result };

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="card">
      <p className="text-xs uppercase tracking-wider text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs text-slate-500">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [state, setState] = useState<Saved | null | undefined>(undefined);
  const [err, setErr] = useState("");

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("analysis");
      setState(raw ? (JSON.parse(raw) as Saved) : null);
    } catch {
      setState(null);
    }
  }, []);

  if (state === undefined) return <main className="p-10 text-center text-slate-400">Loading…</main>;
  if (state === null) {
    return (
      <main className="mx-auto max-w-xl px-4 py-20 text-center">
        <p className="text-slate-300">No analysis yet. Pick an industry to get started.</p>
        <Link href="/" className="btn mt-4">Choose industry</Link>
      </main>
    );
  }

  const { payload, result: r } = state;
  const ai = r.ai;
  const get = async (fmt: "pdf" | "xlsx" | "csv") => {
    try { setErr(""); await downloadReport(fmt, payload, r); }
    catch (e) { setErr(e instanceof Error ? e.message : "Download failed"); }
  };

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold sm:text-3xl">{r.industry} Energy Dashboard</h1>
          <p className="text-sm text-slate-400">
            {r.bill.billing_date ? `Bill date ${r.bill.billing_date} · ` : ""}{r.bill.days} billing days
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn-ghost" onClick={() => get("pdf")}>PDF</button>
          <button className="btn-ghost" onClick={() => get("xlsx")}>Excel</button>
          <button className="btn-ghost" onClick={() => get("csv")}>CSV</button>
          <Link href="/" className="btn">New analysis</Link>
        </div>
      </div>
      {err && <p className="text-sm text-amber-300">{err}</p>}

      <div className={`rounded-xl border p-4 text-sm ${ai.bill_anomaly.is_anomaly
        ? "border-amber-400/40 bg-amber-500/10 text-amber-200"
        : "border-white/10 bg-white/5 text-slate-300"}`}>
        {ai.bill_anomaly.is_anomaly ? "⚠ " : ""}{ai.bill_anomaly.message}
      </div>

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Kpi label="Total units" value={`${num(r.bill.units)} kWh`} />
        <Kpi label="Total amount" value={inr(r.bill.amount)} sub={`${r.rate} ₹/unit`} />
        <Kpi label="Estimated next bill" value={inr(ai.forecast.amount[0])} sub={`${num(ai.forecast.units[0])} kWh`} />
        <Kpi label="Expected peak load" value={`${num(ai.peak_load_kw)} kW`} />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <SharePie rows={r.rows} />
        <CostBar r={r} />
        <TrendLine r={r} />
        <DailyBar r={r} />
        <EfficiencyBar r={r} />
        <div className="card">
          <h3 className="mb-3 font-semibold">Efficiency analysis</h3>
          <dl className="space-y-3 text-sm">
            {[
              ["Highest consumer", r.highest], ["Lowest consumer", r.lowest],
              ["Most efficient machine", r.most_efficient], ["Least efficient machine", r.least_efficient],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between gap-4 border-b border-white/5 pb-2">
                <dt className="text-slate-400">{k}</dt><dd className="font-medium">{v}</dd>
              </div>
            ))}
          </dl>
          <h4 className="mb-2 mt-4 text-sm font-semibold">Abnormal usage</h4>
          {ai.machine_anomalies.length === 0
            ? <p className="text-sm text-slate-400">No abnormal machine usage detected.</p>
            : <ul className="space-y-1 text-sm text-amber-200">
                {ai.machine_anomalies.map((a) => <li key={a.machine}>⚠ {a.message}</li>)}
              </ul>}
        </div>
      </section>

      <section className="card overflow-x-auto">
        <h3 className="mb-3 font-semibold">Machine-wise consumption and cost</h3>
        <table className="w-full min-w-[480px] text-sm">
          <thead className="text-left text-slate-400">
            <tr><th className="py-2">Machine</th><th>Units (kWh)</th><th>Cost</th><th>Share</th></tr>
          </thead>
          <tbody>
            {r.rows.map((x) => (
              <tr key={x.name} className="border-t border-white/5">
                <td className="py-2">{x.name}</td><td>{num(x.units)}</td><td>{inr(x.cost)}</td><td>{x.pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="card">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-semibold">AI recommendations</h3>
          <span className="rounded-full bg-teal-500/15 px-3 py-1 text-sm text-teal-300">
            Estimated savings {inr(ai.total_savings)} / month
          </span>
        </div>
        {ai.recommendations.length === 0
          ? <p className="text-sm text-slate-400">No major issues found. Keep monitoring monthly.</p>
          : <ul className="space-y-3">
              {ai.recommendations.map((t, i) => (
                <li key={i} className="rounded-xl border border-white/10 p-3 text-sm">
                  <p>{t.machine && <b>{t.machine}: </b>}{t.text}</p>
                  <p className="mt-1 text-xs text-teal-300">
                    Saves about {num(t.save_units)} kWh · {inr(t.save_cost)} per month
                  </p>
                </li>
              ))}
            </ul>}
      </section>
    </main>
  );
}