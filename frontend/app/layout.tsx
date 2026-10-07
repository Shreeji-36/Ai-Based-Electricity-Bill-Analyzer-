import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "AI Industrial Energy Intelligence",
  description: "AI Powered Industrial Energy Intelligence Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Header />
        {children}
        <footer className="py-8 text-center text-xs text-slate-500">
          Estimates are based on rated machine power and the hours you enter.
        </footer>
      </body>
    </html>
  );
}