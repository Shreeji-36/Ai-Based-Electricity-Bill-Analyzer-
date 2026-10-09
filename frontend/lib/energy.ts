import { Industry } from "./industries";

export type Bill = { units: number; amount: number; days: number };
export type Row = {
  name: string; units: number; cost: number; pct: number; efficiency: number;
  qty?: number; hours?: number;
};

export function analyze(
  ind: Industry,
  bill: Bill,
  hours: Record<string, number>,
  qty: Record<string, number> = {}
) {
  const rate = bill.units > 0 ? bill.amount / bill.units : ind.rate;
  const days = bill.days || 30;

  let rows: Row[] = ind.machines.map(m => {
    const n = qty[m.id] ?? 1;          // how many machines of this type
    const h = hours[m.id] || 0;        // hours per day for EACH machine
    const units = m.kw * n * h * days * (m.efficiency / 100 + 0.2);
    return { name: m.name, units, cost: 0, pct: 0, efficiency: m.efficiency, qty: n, hours: h };
  });

  // Scale down if estimate exceeds the real bill
  const est = rows.reduce((s, r) => s + r.units, 0);
  if (est > bill.units) rows = rows.map(r => ({ ...r, units: (r.units / est) * bill.units * 0.95 }));

  const machineTotal = rows.reduce((s, r) => s + r.units, 0);
  rows.push({ name: "Others", units: Math.max(bill.units - machineTotal, 0), cost: 0, pct: 0, efficiency: 90, qty: 0, hours: 0 });

  rows = rows.map(r => ({
    ...r,
    units: Math.round(r.units),
    cost: Math.round(r.units * rate),
    pct: +((r.units / bill.units) * 100).toFixed(1),
  }));

  const named = rows.filter(r => r.name !== "Others");
  const top = [...named].sort((a, b) => b.units - a.units)[0];
  const low = [...named].sort((a, b) => a.units - b.units)[0];
  const best = [...named].sort((a, b) => b.efficiency - a.efficiency)[0];
  const worst = [...named].sort((a, b) => a.efficiency - b.efficiency)[0];

  // Simple forecast: +3% trend (replaced by ML model in ai-engine later)
  const nextUnits = Math.round(bill.units * 1.03);
  const nextBill = Math.round(nextUnits * rate);

  const tips = named.filter(r => r.efficiency < 78 || r.pct > 25).map(r => {
    const saveUnits = Math.round(r.units * 0.12);
    return { text: `Optimize ${r.name}: reduce idle time and schedule maintenance.`,
             saveUnits, saveCost: Math.round(saveUnits * rate) };
  });

  return { rows, rate, top, low, best, worst, nextUnits, nextBill, tips,
           totalSavings: tips.reduce((s, t) => s + t.saveCost, 0) };
}