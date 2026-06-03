import { env } from "@/lib/env";
import { formatApiError } from "@/lib/api/errors";

export type DocumentRecord = {
  id: string;
  owner_id: string;
  title: string;
  description: string | null;
  category: string;
  storage_bucket: string;
  storage_path: string;
  mime_type: string;
  file_size_bytes: number;
  checksum_sha256: string | null;
  status: string;
  error_message: string | null;
  uploaded_at: string;
  updated_at: string;
};

export type DocumentPageRecord = {
  id: string;
  document_id: string;
  page_number: number;
  text_content: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type DocumentChunkRecord = {
  id: string;
  document_id: string;
  page_id: string | null;
  chunk_index: number;
  content: string;
  token_count: number | null;
  page_start: number | null;
  page_end: number | null;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type DocumentDetailRecord = {
  document: DocumentRecord;
  page_count: number;
  chunk_count: number;
  embedding_count: number;
  vector_count: number;
  embedding_model: string | null;
  pages: DocumentPageRecord[];
  chunks: DocumentChunkRecord[];
};

async function apiFetch<T>(
  path: string,
  accessToken: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(formatApiError(body, `Request failed (${response.status})`));
  }

  return body as T;
}

export async function fetchMyDocuments(accessToken: string): Promise<DocumentRecord[]> {
  return apiFetch<DocumentRecord[]>("/documents", accessToken);
}

export async function fetchDocumentDetail(
  accessToken: string,
  documentId: string
): Promise<DocumentDetailRecord> {
  return apiFetch<DocumentDetailRecord>(`/documents/${documentId}`, accessToken);
}

export async function parseDocument(
  accessToken: string,
  documentId: string
): Promise<{ document: DocumentRecord; message: string }> {
  return apiFetch<{ document: DocumentRecord; message: string }>(
    `/documents/${documentId}/parse`,
    accessToken,
    { method: "POST" }
  );
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function formatDocumentStatus(status: string): string {
  return status.replaceAll("_", " ");
}

export function statusBadgeClass(status: string): string {
  switch (status) {
    case "ready":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    case "processing":
      return "bg-amber-50 text-amber-800 border-amber-200";
    case "failed":
      return "bg-red-50 text-red-700 border-red-200";
    case "uploaded":
      return "bg-slate-100 text-slate-700 border-slate-200";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}
