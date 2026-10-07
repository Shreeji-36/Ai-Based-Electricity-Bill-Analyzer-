import Link from "next/link";
import Logo from "@/components/Logo";
import { INDUSTRIES } from "@/lib/industries";

const STEPS = [
  ["1", "Upload your bill", "JPG, PNG or PDF. We read the units and amount."],
  ["2", "Enter machine hours", "Just the average daily running hours."],
  ["3", "Get AI insights", "Costs, forecast, anomalies and savings."],
];

export default function Home() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-14 text-center">
      <div className="mx-auto mb-5 w-fit"><Logo size={72} /></div>
      <h1 className="text-3xl font-bold sm:text-5xl">AI Industrial Energy Intelligence</h1>
      <p className="mt-3 text-lg text-teal-300">AI Powered Industrial Energy Intelligence Platform</p>
      <p className="mx-auto mt-4 max-w-2xl text-slate-400">
        See which machines use the most electricity, predict next month&apos;s bill and
        get recommendations that cut your cost.
      </p>

      <h2 className="mt-12 text-sm font-semibold uppercase tracking-widest text-slate-400">
        Choose your industry
      </h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {INDUSTRIES.map((i) => (
          <Link key={i.id} href={`/industry/${i.id}`}
            className="card group text-left transition hover:-translate-y-1 hover:border-teal-400/60">
            <div className="text-4xl">{i.icon}</div>
            <h3 className="mt-3 text-xl font-semibold group-hover:text-teal-300">{i.name}</h3>
            <p className="mt-1 text-sm text-slate-400">{i.desc}</p>
          </Link>
        ))}
      </div>

      <div className="mt-12 grid gap-3 sm:grid-cols-3">
        {STEPS.map(([n, t, d]) => (
          <div key={n} className="rounded-xl border border-white/10 p-4 text-left">
            <span className="text-xs font-bold text-teal-300">STEP {n}</span>
            <p className="mt-1 font-medium">{t}</p>
            <p className="text-sm text-slate-400">{d}</p>
          </div>
        ))}
      </div>
    </main>
  );
}