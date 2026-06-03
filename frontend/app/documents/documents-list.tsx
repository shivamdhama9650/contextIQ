"use client";

import { FileText, Loader2, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { formatApiError } from "@/lib/api/errors";
import {
  type DocumentRecord,
  formatDocumentStatus,
  formatFileSize,
  statusBadgeClass
} from "@/lib/api/documents";
import { createClient } from "@/lib/supabase/browser";

type LoadState = {
  documents: DocumentRecord[];
  error: string | null;
  isLoading: boolean;
};

export function DocumentsList() {
  const [state, setState] = useState<LoadState>({
    documents: [],
    error: null,
    isLoading: true
  });

  async function loadDocuments() {
    setState((current) => ({ ...current, error: null, isLoading: true }));

    try {
      const supabase = createClient();
      const {
        data: { user },
        error: userError
      } = await supabase.auth.getUser();

      if (userError || !user) {
        setState({
          documents: [],
          error: "Your session has expired. Please sign in again.",
          isLoading: false
        });
        return;
      }

      const { data, error } = await supabase
        .from("documents")
        .select(
          "id, owner_id, title, description, category, storage_bucket, storage_path, mime_type, file_size_bytes, checksum_sha256, status, error_message, uploaded_at, updated_at"
        )
        .eq("owner_id", user.id)
        .order("uploaded_at", { ascending: false });

      if (error) {
        setState({
          documents: [],
          error: formatApiError({ detail: error.message }, "Could not load your documents."),
          isLoading: false
        });
        return;
      }

      setState({
        documents: (data ?? []) as DocumentRecord[],
        error: null,
        isLoading: false
      });
    } catch {
      setState({
        documents: [],
        error: "Could not reach the document service. Try again in a moment.",
        isLoading: false
      });
    }
  }

  useEffect(() => {
    void loadDocuments();
  }, []);

  if (state.isLoading) {
    return (
      <div className="mt-8 rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex items-center gap-3 text-sm text-slate-600">
          <Loader2 aria-hidden="true" className="animate-spin text-accent" size={18} />
          Loading your documents...
        </div>
        <div className="mt-6 space-y-3">
          {[0, 1, 2].map((item) => (
            <div className="h-12 rounded-md bg-slate-100" key={item} />
          ))}
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="mt-8 rounded-lg border border-red-200 bg-red-50 p-6">
        <p className="text-sm text-red-700">{state.error}</p>
        <button
          className="mt-4 inline-flex items-center gap-2 rounded-md border border-red-200 bg-white px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-50"
          onClick={() => void loadDocuments()}
          type="button"
        >
          <RefreshCw aria-hidden="true" size={16} />
          Retry
        </button>
      </div>
    );
  }

  if (state.documents.length === 0) {
    return (
      <div className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-accent">
          <FileText aria-hidden="true" size={22} />
        </div>
        <h2 className="mt-4 text-lg font-semibold">No documents yet</h2>
        <p className="mt-2 text-sm text-slate-600">
          Upload your first company PDF to parse, embed, and index it for chat.
        </p>
        <Link
          className="mt-5 inline-flex rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
          href="/documents/upload"
        >
          Upload your first PDF
        </Link>
      </div>
    );
  }

  return (
    <div className="mt-8 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
        <p className="text-sm font-semibold text-slate-700">
          {state.documents.length} document{state.documents.length === 1 ? "" : "s"}
        </p>
        <button
          className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50"
          onClick={() => void loadDocuments()}
          type="button"
        >
          <RefreshCw aria-hidden="true" size={14} />
          Refresh
        </button>
      </div>
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
          {state.documents.map((document) => (
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
  );
}
