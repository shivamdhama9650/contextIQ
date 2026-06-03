import { Upload } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { createClient } from "@/lib/supabase/server";

import { DocumentsList } from "./documents-list";

export default async function DocumentsPage() {
  const supabase = await createClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-5xl">
        <div className="flex flex-col gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-accent">
              Document knowledge base
            </p>
            <h1 className="mt-2 text-3xl font-semibold">My documents</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              PDFs are parsed, chunked, embedded, and indexed so the assistant
              can answer with grounded sources.
            </p>
          </div>
          <Link
            className="inline-flex items-center justify-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
            href="/documents/upload"
          >
            <Upload aria-hidden="true" size={16} />
            Upload PDF
          </Link>
        </div>

        <DocumentsList />
      </section>
    </main>
  );
}
