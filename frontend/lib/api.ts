import { getToken } from "./auth";
import { getIndustry } from "./industries";
import { analyze as local } from "./energy";

export const API = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

export type Payload = {
  industry: string;
  bill: {
    units: number; amount: number; days: number;
    consumer_number?: string; tariff?: string; billing_date?: string;
  };
  hours: Record<string, number>;
  qty: Record<string, number>;
};

export type Row = {
  id?: string; name: string; units: number; cost: number; pct: number; efficiency: number;
  qty?: number; hours?: number;
};

export type Result = {
  industry: string;
  bill: { units: number; amount: number; days: number; billing_date?: string | null };
  rate: number;
  rows: Row[];
  estimate?: { raw_units: number; scaled: boolean };
  highest: string; lowest: string; most_efficient: string; least_efficient: string;
  forecast: { units: number; amount: number };
  tips: { text: string; save_units: number; save_cost: number }[];
  total_savings: number;
  ai: {
    forecast: { method: string; units: number[]; low: number[]; high: number[]; amount: number[] };
    peak_load_kw: number;
    bill_anomaly: { is_anomaly: boolean; score: number; method: string; message: string };
    machine_anomalies: { machine: string; share: number; expected: number; message: string }[];
        recommendations: { machine: string; text: string; kind?: string; save_units: number; save_cost: number }[];
    total_savings: number;
  };
};

export type OcrResult = {
  consumer_number: string | null; billing_date: string | null; tariff: string | null;
    units: number | null; amount: number | null; days: number | null; confidence: number;
  units_unit?: string | null; warnings?: string[];
};

const authHeader = (): Record<string, string> => {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
};

async function fail(res: Response, fallback: string): Promise<never> {
  const body = await res.json().catch(() => ({}));
  throw new Error(typeof body.detail === "string" ? body.detail : fallback);
}

/* ---------- Demo mode (no backend): same shape as the API result ---------- */
function demo(p: Payload): Result {
  const ind = getIndustry(p.industry)!;
  const r = local(ind, p.bill, p.hours, p.qty);
  const f = [1, 2, 3].map((i) => Math.round(p.bill.units * Math.pow(1.03, i)));
  const tips = r.tips.map((t) => ({ text: t.text, save_units: t.saveUnits, save_cost: t.saveCost }));
  return {
    industry: ind.name,
    bill: p.bill,
    rate: +r.rate.toFixed(2),
    rows: r.rows,
    estimate: { raw_units: r.rawUnits, scaled: r.rawUnits > p.bill.units },
    highest: r.top.name, lowest: r.low.name,
    most_efficient: r.best.name, least_efficient: r.worst.name,
    forecast: { units: r.nextUnits, amount: r.nextBill },
    tips,
    total_savings: r.totalSavings,
    ai: {
      forecast: {
        method: "demo-trend", units: f,
        low: f.map((v) => Math.round(v * 0.93)),
        high: f.map((v) => Math.round(v * 1.07)),
        amount: f.map((v) => Math.round(v * r.rate)),
      },
      peak_load_kw: Math.round(
        ind.machines.reduce((s, m) => s + ((p.hours[m.id] || 0) > 0 ? m.kw * (p.qty?.[m.id] ?? 1) * 0.85 : 0), 0)
      ),
      bill_anomaly: {
        is_anomaly: false, score: 0, method: "demo",
        message: "Sign in and add more monthly bills to enable anomaly detection.",
      },
      machine_anomalies: [],
      recommendations: tips.map((t) => ({ machine: "", ...t })),
      total_savings: r.totalSavings,
    },
  };
}

export async function runAnalysis(p: Payload): Promise<Result> {
  if (!API) return demo(p);
  const token = getToken();
  // Signed in: saved analysis. Not signed in: public preview (nothing is saved).
  const url = token ? `${API}/api/analysis` : `${API}/api/analysis/preview`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader() },
      body: JSON.stringify(p),
    });
    if (!res.ok) return await fail(res, "Please check your inputs and try again.");
    return await res.json();
  } catch (e) {
    // Backend unreachable and not signed in: fall back to the offline demo
    if (!token && e instanceof TypeError) return demo(p);
    throw e;
  }
}

export async function uploadBill(file: File): Promise<OcrResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/api/bills/upload`, { method: "POST", headers: authHeader(), body: form });
  if (!res.ok) return fail(res, "Could not read this bill. Please enter the values manually.");
  return res.json();
}

export async function authRequest(
  mode: "login" | "register", f: { name: string; email: string; password: string }
): Promise<string> {
  const res =
    mode === "login"
      ? await fetch(`${API}/api/auth/login`, {
          method: "POST",
          body: new URLSearchParams({ username: f.email, password: f.password }),
        })
      : await fetch(`${API}/api/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(f),
        });
  if (!res.ok) return fail(res, "Please check your details (password needs 8+ characters).");
  return (await res.json()).access_token;
}

function save(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name; a.click();
  URL.revokeObjectURL(url);
}

export async function downloadReport(fmt: "pdf" | "xlsx" | "csv", p: Payload, r: Result) {
  if (API && getToken()) {
    const res = await fetch(`${API}/api/reports/${fmt}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader() },
      body: JSON.stringify(p),
    });
    if (!res.ok) return fail(res, "Could not generate the report.");
    return save(await res.blob(), `energy-report.${fmt}`);
  }
  if (fmt !== "csv") throw new Error("Sign in to download PDF and Excel reports. CSV works without signing in.");
  const lines = [
    ["Machine", "Units (kWh)", "Cost (INR)", "Share (%)", "Efficiency (%)"],
    ...r.rows.map((x) => [`"${x.name}"`, x.units, x.cost, x.pct, x.efficiency]),
  ].map((l) => l.join(",")).join("\n");
  save(new Blob([lines], { type: "text/csv" }), "energy-report.csv");
}