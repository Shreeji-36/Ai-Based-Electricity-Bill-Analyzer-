"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { API, authRequest } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      setToken(await authRequest(mode, f));
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-md px-4 py-16">
      <form onSubmit={submit} className="card space-y-4">
        <h1 className="text-2xl font-bold">{mode === "login" ? "Sign in" : "Create account"}</h1>

        {!API && (
          <p className="rounded-lg bg-amber-500/10 p-3 text-sm text-amber-300">
            No backend is connected, so the app runs in demo mode. You can use it without signing in.
          </p>
        )}

        {mode === "register" && (
          <div>
            <label className="label">Name</label>
            <input className="input" required minLength={2} value={f.name}
              onChange={(e) => setF({ ...f, name: e.target.value })} />
          </div>
        )}
        <div>
          <label className="label">Email</label>
          <input className="input" type="email" required value={f.email}
            onChange={(e) => setF({ ...f, email: e.target.value })} />
        </div>
        <div>
          <label className="label">Password</label>
          <input className="input" type="password" required minLength={8} value={f.password}
            onChange={(e) => setF({ ...f, password: e.target.value })} />
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}
        <button className="btn w-full" disabled={busy || !API}>
          {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Register"}
        </button>

        <button type="button" className="w-full text-sm text-slate-400 hover:text-white"
          onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
          {mode === "login" ? "New here? Create an account" : "Already have an account? Sign in"}
        </button>
        <Link href="/" className="block text-center text-sm text-teal-300">Continue in demo mode →</Link>
      </form>
    </main>
  );
}