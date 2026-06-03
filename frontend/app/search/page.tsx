import { redirect } from "next/navigation";

import { createClient } from "@/lib/supabase/server";

import { SearchForm } from "./search-form";

export default async function SearchPage() {
  const supabase = await createClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-3xl">
        <p className="text-sm font-semibold uppercase tracking-wide text-accent">
          Knowledge retrieval
        </p>
        <h1 className="mt-2 text-3xl font-semibold">Semantic search</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          Search your uploaded company documents by meaning using the indexed
          knowledge base.
        </p>

        <div className="mt-8">
          <SearchForm />
        </div>
      </section>
    </main>
  );
}
