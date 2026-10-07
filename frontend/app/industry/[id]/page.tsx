"use client";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { API, runAnalysis, uploadBill, type Payload } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { getIndustry, type Industry } from "@/lib/industries";

export default function IndustryPage() {
  const { id } = useParams<{ id: string }>();
  const ind = getIndustry(id);
  if (!ind) {
    return (
      <main className="mx-auto max-w-xl px-4 py-20 text-center">
        <p>Industry not found.</p>
        <Link href="/" className="btn mt-4">Back home</Link>
      </main>
    );
  }
  return <Wizard ind={ind} />;
}

function Wizard({ ind }: { ind: Industry }) {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [bill, setBill] = useState({
    consumer_number: "", billing_date: "", tariff: "", units: "", amount: "", days: "30",
  });
  const [hours, setHours] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  async function onFile(file?: File) {
    if (!file) return;
    setError(""); setMsg("");
    if (!/\.(jpe?g|png|pdf)$/i.test(file.name)) return setError("Please choose a JPG, PNG or PDF file.");
    if (file.size > 8 * 1024 * 1024) return setError("File is too large (max 8 MB).");
    if (!API || !getToken()) {
      return setMsg("Sign in to enable automatic bill reading. For now, enter the values below.");
    }
    setBusy(true);
    try {
      const d = await uploadBill(file);
      setBill((b) => ({
        consumer_number: d.consumer_number ?? b.consumer_number,
        billing_date: d.billing_date ?? b.billing_date,
        tariff: d.tariff ?? b.tariff,
        units: d.units != null ? String(d.units) : b.units,
        amount: d.amount != null ? String(d.amount) : b.amount,
        days: d.days != null ? String(d.days) : b.days,
      }));
      setMsg(`Bill read (confidence ${Math.round((d.confidence ?? 0) * 100)}%). Please check the values.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  function toStep2() {
    const u = Number(bill.units), a = Number(bill.amount), d = Number(bill.days);
    if (!(u > 0) || !(a > 0)) return setError("Enter total units and total bill amount (both above 0).");
    if (!(d >= 1 && d <= 62)) return setError("Billing days must be between 1 and 62.");
    setError(""); setStep(2);
  }

  async function submit() {
    const h: Record<string, number> = {};
    for (const m of ind.machines) {
      const v = Number(hours[m.id] || 0);
      if (!(v >= 0 && v <= 24)) return setError(`${m.name}: hours must be between 0 and 24.`);
      h[m.id] = v;
    }
    if (Object.values(h).every((v) => v === 0)) return setError("Enter hours for at least one machine.");

    const payload: Payload = {
      industry: ind.id,
      bill: {
        units: Number(bill.units), amount: Number(bill.amount), days: Number(bill.days),
        consumer_number: bill.consumer_number || undefined,
        tariff: bill.tariff || undefined,
        billing_date: bill.billing_date || undefined,
      },
      hours: h,
    };
    setBusy(true); setError("");
    try {
      const result = await runAnalysis(payload);
      sessionStorage.setItem("analysis", JSON.stringify({ payload, result }));
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
      setBusy(false);
    }
  }

  const field = (key: keyof typeof bill, label: string, type = "text", ph = "") => (
    <div>
      <label className="label">{label}</label>
      <input className="input" type={type} placeholder={ph} value={bill[key]}
        onChange={(e) => setBill({ ...bill, [key]: e.target.value })} />
    </div>
  );

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <Link href="/" className="text-sm text-slate-400 hover:text-white">← All industries</Link>
      <h1 className="mt-3 text-3xl font-bold">{ind.icon} {ind.name} Energy Analysis</h1>
      <p className="mt-1 text-sm text-slate-400">Step {step} of 2</p>

      <div className="card mt-6 space-y-5">
        {step === 1 ? (
          <>
            <h2 className="text-lg font-semibold">Electricity bill</h2>
            <div>
              <label className="label">Upload bill (JPG, PNG, PDF), optional</label>
              <input type="file" accept=".jpg,.jpeg,.png,.pdf"
                onChange={(e) => onFile(e.target.files?.[0])}
                className="block w-full text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-teal-500 file:px-4 file:py-2 file:font-semibold file:text-slate-950" />
              {busy && <p className="mt-2 text-sm text-slate-400">Reading bill…</p>}
              {msg && <p className="mt-2 text-sm text-teal-300">{msg}</p>}
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {field("consumer_number", "Consumer number")}
              {field("billing_date", "Billing date", "text", "DD/MM/YYYY")}
              {field("tariff", "Tariff")}
              {field("days", "Billing days *", "number")}
              {field("units", "Total units (kWh) *", "number", "e.g. 20000")}
              {field("amount", "Total bill amount (₹) *", "number", "e.g. 170000")}
            </div>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <button className="btn w-full" onClick={toStep2} disabled={busy}>Continue</button>
          </>
        ) : (
          <>
            <h2 className="text-lg font-semibold">Average hours used per day</h2>
            <div className="space-y-3">
              {ind.machines.map((m) => (
                <div key={m.id} className="flex items-center justify-between gap-4">
                  <label className="text-sm">{m.name}</label>
                  <input className="input !w-28 text-right" type="number" min={0} max={24} step={0.5}
                    placeholder="hrs" value={hours[m.id] ?? ""}
                    onChange={(e) => setHours({ ...hours, [m.id]: e.target.value })} />
                </div>
              ))}
              <div className="flex items-center justify-between gap-4 text-slate-500">
                <span className="text-sm">Others</span>
                <span className="text-sm">Auto calculated</span>
              </div>
            </div>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <div className="flex gap-3">
              <button className="btn-ghost" onClick={() => { setStep(1); setError(""); }}>Back</button>
              <button className="btn flex-1" onClick={submit} disabled={busy}>
                {busy ? "Analyzing…" : "Analyze energy usage"}
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  );
}