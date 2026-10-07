"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { clearToken, getToken } from "@/lib/auth";
import Logo from "./Logo";

export default function Header() {
  const [signedIn, setSignedIn] = useState(false);
  useEffect(() => {
    setSignedIn(!!getToken());
  }, []);

  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Logo size={28} />
          <span className="hidden sm:inline">AI Industrial Energy Intelligence</span>
        </Link>
        {signedIn ? (
          <button className="btn-ghost" onClick={() => { clearToken(); location.href = "/"; }}>
            Sign out
          </button>
        ) : (
          <Link href="/login" className="btn-ghost">Sign in</Link>
        )}
      </div>
    </header>
  );
}