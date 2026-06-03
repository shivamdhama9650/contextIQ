import { FileText, Upload } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import {
  type DocumentRecord,
  fetchMyDocuments,
  formatDocumentStatus,
  formatFileSize,
  statusBadgeClass
} from "@/lib/api/documents";
import { createClient } from "@/lib/supabase/server";

export default async function DocumentsPage() {
  const supabase = await createClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    redirect("/auth/login");
  }

  let documents: DocumentRecord[] = [];
  let loadError: string | null = null;

  try {
    documents = await fetchMyDocuments(session.access_token);
  } catch {
    loadError = "Could not load your documents. Check that the backend is running.";
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

        {loadError ? (
          <p className="mt-8 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {loadError}
          </p>
        ) : null}

        {!loadError && documents.length === 0 ? (
          <div className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-accent">
              <FileText aria-hidden="true" size={22} />
            </div>
            <h2 className="mt-4 text-lg font-semibold">No documents yet</h2>
            <p className="mt-2 text-sm text-slate-600">
              Upload your first company PDF to parse and store page text.
            </p>
            <Link
              className="mt-5 inline-flex rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              href="/documents/upload"
            >
              Upload your first PDF
            </Link>
          </div>
        ) : null}

        {!loadError && documents.length > 0 ? (
          <div className="mt-8 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Size</th>
                  <th className="px-4 py-3">Uploaded</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {documents.map((document) => (
                  <tr key={document.id}>
                    <td className="px-4 py-4 font-medium">{document.title}</td>
                    <td className="px-4 py-4 capitalize text-slate-600">{document.category}</td>
                    <td className="px-4 py-4">
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold capitalize ${statusBadgeClass(document.status)}`}
                      >
                        {formatDocumentStatus(document.status)}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-slate-600">
                      {formatFileSize(document.file_size_bytes)}
                    </td>
                    <td className="px-4 py-4 text-slate-600">
                      {new Date(document.uploaded_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-4">
                      <Link
                        className="font-semibold text-accent hover:underline"
                        href={`/documents/${document.id}`}
                      >
                        View pages
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </main>
  );
}
