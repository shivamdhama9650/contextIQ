import Link from "next/link";
import { redirect } from "next/navigation";

import { createClient } from "@/lib/supabase/server";

import { UploadDocumentForm } from "./upload-document-form";

export default async function UploadDocumentPage() {
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
          Secure document upload
        </p>
        <h1 className="mt-2 text-3xl font-semibold">Upload company document</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
          Upload a PDF and the backend will extract text, create searchable
          chunks, generate embeddings, and index it for grounded answers.
        </p>

        <Link
          className="mt-4 inline-block text-sm font-semibold text-accent hover:underline"
          href="/documents"
        >
          View my uploaded documents
        </Link>

        <UploadDocumentForm />
      </section>
    </main>
  );
}
