import React from "react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { MessageSquare, ArrowLeft, Shield } from "lucide-react";
import { createClient } from "@/lib/supabase/server";
import { ChatWindow } from "../components/ChatWindow";

export default async function ChatPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-800 px-4 py-8 sm:px-6 md:py-10">
      <div className="mx-auto max-w-5xl">
        {/* Navigation & Header */}
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-200/80 pb-5">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:bg-slate-50 hover:text-slate-900"
            >
              <ArrowLeft size={16} />
            </Link>
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-600 uppercase tracking-wider">
                  Live knowledge chat
                </span>
                <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                  <Shield size={10} /> Grounded
                </span>
              </div>
              <h1 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl text-slate-900 flex items-center gap-2">
                <MessageSquare className="text-blue-600 animate-pulse" size={24} />
                Knowledge Assistant
              </h1>
            </div>
          </div>

          <div className="flex flex-wrap gap-2.5">
            <Link
              className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-xs font-semibold shadow-sm transition hover:bg-slate-50"
              href="/dashboard"
            >
              Dashboard
            </Link>
            <Link
              className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-xs font-semibold shadow-sm transition hover:bg-slate-50"
              href="/search"
            >
              Knowledge Search
            </Link>
            <Link
              className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-xs font-semibold shadow-sm transition hover:bg-slate-50"
              href="/documents"
            >
              My Documents
            </Link>
          </div>
        </header>

        {/* Chat Interface Container */}
        <section className="relative">
          {/* Ambient Glow Effects */}
          <div className="absolute -left-20 -top-20 h-72 w-72 rounded-full bg-blue-400/10 blur-3xl"></div>
          <div className="absolute -right-20 -bottom-20 h-72 w-72 rounded-full bg-indigo-400/10 blur-3xl"></div>

          <ChatWindow />
        </section>
      </div>
    </main>
  );
}

export const metadata = {
  title: "Grounded Chat Assistant | Enterprise Knowledge Assistant",
  description: "Chat in real-time with internal company documentation using verified sources.",
};
