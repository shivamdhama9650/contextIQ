import Link from "next/link";
import { redirect } from "next/navigation";

import {
  type DocumentChunkRecord,
  type DocumentPageRecord,
  type DocumentRecord,
  formatDocumentStatus,
  statusBadgeClass
} from "@/lib/api/documents";
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

  let document: DocumentRecord | null = null;
  let pages: DocumentPageRecord[] = [];
  let chunks: DocumentChunkRecord[] = [];
  let embeddingCount = 0;
  let loadError: string | null = null;

  const { data: documentData, error: documentError } = await supabase
    .from("documents")
    .select(
      "id, owner_id, title, description, category, storage_bucket, storage_path, mime_type, file_size_bytes, checksum_sha256, status, error_message, uploaded_at, updated_at"
    )
    .eq("id", id)
    .maybeSingle();

  if (documentError) {
    loadError = documentError.message;
  } else if (!documentData) {
    loadError = "This document does not exist, or your account does not have access to it.";
  } else {
    document = documentData as DocumentRecord;

    const [pagesResult, chunksResult, embeddingsResult] = await Promise.all([
      supabase
        .from("document_pages")
        .select("id, document_id, page_number, text_content, metadata, created_at")
        .eq("document_id", id)
        .order("page_number", { ascending: true }),
      supabase
        .from("document_chunks")
        .select(
          "id, document_id, page_id, chunk_index, content, token_count, page_start, page_end, metadata, created_at"
        )
        .eq("document_id", id)
        .order("chunk_index", { ascending: true })
        .limit(20),
      supabase
        .from("chunk_embeddings")
        .select("id", { count: "exact", head: true })
        .eq("document_id", id)
    ]);

    if (pagesResult.error) {
      loadError = pagesResult.error.message;
    } else if (chunksResult.error) {
      loadError = chunksResult.error.message;
    } else if (embeddingsResult.error) {
      loadError = embeddingsResult.error.message;
    } else {
      pages = (pagesResult.data ?? []) as DocumentPageRecord[];
      chunks = (chunksResult.data ?? []) as DocumentChunkRecord[];
      embeddingCount = embeddingsResult.count ?? 0;
    }
  }

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
              <span className="text-sm text-slate-600">{pages.length} page(s)</span>
              <span className="text-sm text-slate-600">{chunks.length} chunk preview(s)</span>
              <span className="text-sm text-slate-600">{embeddingCount} embedding(s)</span>
            </div>

            {document.error_message ? (
              <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {document.error_message}
              </p>
            ) : null}

            {document.status === "uploaded" ? (
              <p className="mt-4 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
                This file was uploaded successfully. Run parsing to extract pages, create chunks,
                and make it searchable in chat.
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

            {chunks.length ? (
              <div className="mt-8">
                <h2 className="text-lg font-semibold">Search chunks (preview)</h2>
                <p className="mt-1 text-sm text-slate-600">
                  Text chunks are embedded and indexed for semantic search.
                </p>
                <div className="mt-4 space-y-3">
                  {chunks.map((chunk) => (
                    <article
                      className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                      key={chunk.id}
                    >
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Chunk {chunk.chunk_index + 1}
                        {chunk.page_start
                          ? ` - page ${chunk.page_start}${chunk.page_end && chunk.page_end !== chunk.page_start ? `-${chunk.page_end}` : ""}`
                          : ""}
                        {chunk.token_count ? ` - ~${chunk.token_count} tokens` : ""}
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
              {pages.length ? (
                pages.map((page) => (
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
                  No page text is stored yet. If this document was just uploaded, use
                  &quot;Run parsing&quot; to extract readable PDF text. If parsing already failed,
                  the PDF may be scanned or image-only and may need OCR in a later phase.
                </p>
              )}
            </div>
          </>
        ) : null}
      </section>
    </main>
  );
}
