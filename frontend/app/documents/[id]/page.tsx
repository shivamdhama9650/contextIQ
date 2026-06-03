import Link from "next/link";
import { redirect } from "next/navigation";

import { fetchDocumentDetail, formatDocumentStatus, statusBadgeClass } from "@/lib/api/documents";
import { createClient } from "@/lib/supabase/server";

import { ReparseDocumentButton } from "../reparse-document-button";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function DocumentDetailPage({ params }: Props) {
  const { id } = await params;
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

  let detail = null;
  let loadError: string | null = null;

  try {
    detail = await fetchDocumentDetail(session.access_token, id);
  } catch {
    loadError = "Could not load this document. It may not exist or the backend is offline.";
  }

  const document = detail?.document;
  const showParseButton =
    document?.status === "uploaded" ||
    document?.status === "failed" ||
    document?.status === "processing";

  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-4xl">
        <Link className="text-sm font-semibold text-accent hover:underline" href="/documents">
          Back to my documents
        </Link>

        {loadError ? (
          <p className="mt-6 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {loadError}
          </p>
        ) : null}

        {document ? (
          <>
            <p className="mt-6 text-sm font-semibold uppercase tracking-wide text-accent">
              Indexed document
            </p>
            <h1 className="mt-2 text-3xl font-semibold">{document.title}</h1>
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <span
                className={`rounded-full border px-3 py-1 text-xs font-semibold capitalize ${statusBadgeClass(document.status)}`}
              >
                {formatDocumentStatus(document.status)}
              </span>
              <span className="text-sm capitalize text-slate-600">{document.category}</span>
              <span className="text-sm text-slate-600">
                {detail?.page_count ?? 0} page(s)
              </span>
              <span className="text-sm text-slate-600">
                {detail?.chunk_count ?? 0} chunk(s)
              </span>
              <span className="text-sm text-slate-600">
                {detail?.embedding_count ?? 0} embedding(s)
              </span>
              <span className="text-sm text-slate-600">
                {detail?.vector_count ?? 0} indexed vector(s)
              </span>
              {detail?.embedding_model ? (
                <span className="text-xs text-slate-500">{detail.embedding_model}</span>
              ) : null}
            </div>

            {document.error_message ? (
              <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {document.error_message}
              </p>
            ) : null}

            {showParseButton ? (
              <div className="mt-6">
                <ReparseDocumentButton
                  documentId={document.id}
                  label={document.status === "failed" ? "Retry parsing" : "Run parsing"}
                />
              </div>
            ) : null}

            {detail?.chunks.length ? (
              <div className="mt-8">
                <h2 className="text-lg font-semibold">Search chunks (preview)</h2>
                <p className="mt-1 text-sm text-slate-600">
                  Text chunks are embedded and indexed for semantic search.
                </p>
                <div className="mt-4 space-y-3">
                  {detail.chunks.map((chunk) => (
                    <article
                      className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                      key={chunk.id}
                    >
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Chunk {chunk.chunk_index + 1}
                        {chunk.page_start
                          ? ` · page ${chunk.page_start}${chunk.page_end && chunk.page_end !== chunk.page_start ? `–${chunk.page_end}` : ""}`
                          : ""}
                        {chunk.token_count ? ` · ~${chunk.token_count} tokens` : ""}
                      </p>
                      <p className="mt-2 line-clamp-4 whitespace-pre-wrap text-sm text-slate-700">
                        {chunk.content}
                      </p>
                    </article>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="mt-8 space-y-4">
              <h2 className="text-lg font-semibold">Full pages</h2>
              {detail?.pages.length ? (
                detail.pages.map((page) => (
                  <article
                    className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
                    key={page.id}
                  >
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                      Page {page.page_number}
                    </h3>
                    <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                      {page.text_content || (
                        <span className="italic text-slate-400">No text on this page.</span>
                      )}
                    </p>
                  </article>
                ))
              ) : (
                <p className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-600">
                  No page text stored yet. Use &quot;Run parsing&quot; to process this document.
                </p>
              )}
            </div>
          </>
        ) : null}
      </section>
    </main>
  );
}
