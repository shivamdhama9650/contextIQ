"use client";

import { FileUp, Loader2 } from "lucide-react";
import { useState } from "react";

import { createClient } from "@/lib/supabase/browser";

const categories = [
  { label: "General", value: "general" },
  { label: "HR", value: "hr" },
  { label: "DevOps", value: "devops" },
  { label: "Security", value: "security" },
  { label: "Finance", value: "finance" },
  { label: "Technical", value: "technical" }
];

const DOCUMENT_BUCKET = "company-documents";
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

type UploadState = {
  status: "idle" | "uploading" | "success" | "error";
  message: string | null;
};

export function UploadDocumentForm() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileInputKey, setFileInputKey] = useState(0);
  const [category, setCategory] = useState("general");
  const [description, setDescription] = useState("");
  const [uploadState, setUploadState] = useState<UploadState>({
    status: "idle",
    message: null
  });

  async function handleUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile) {
      setUploadState({
        status: "error",
        message: "Choose a PDF file before uploading."
      });
      return;
    }

    const validationError = await validatePdf(selectedFile);
    if (validationError) {
      setUploadState({
        status: "error",
        message: validationError
      });
      return;
    }

    setUploadState({ status: "uploading", message: null });

    const supabase = createClient();
    const {
      data: { session }
    } = await supabase.auth.getSession();

    if (!session?.access_token) {
      setUploadState({
        status: "error",
        message: "Your session is missing. Sign in again before uploading."
      });
      return;
    }

    const documentId = crypto.randomUUID();
    const filename = sanitizeFilename(selectedFile.name || "document.pdf");
    const storagePath = `${session.user.id}/${documentId}/${filename}`;
    const checksum = await sha256Hex(selectedFile);
    const title =
      filename
        .replace(/\.pdf$/i, "")
        .replaceAll("-", " ")
        .replaceAll("_", " ")
        .trim() || "Uploaded document";

    const { error: uploadError } = await supabase.storage
      .from(DOCUMENT_BUCKET)
      .upload(storagePath, selectedFile, {
        contentType: "application/pdf",
        upsert: false
      });

    if (uploadError) {
      setUploadState({
        status: "error",
        message: uploadError.message
      });
      return;
    }

    const { error: insertError } = await supabase.from("documents").insert({
      id: documentId,
      owner_id: session.user.id,
      title,
      description: description.trim() || null,
      category,
      storage_bucket: DOCUMENT_BUCKET,
      storage_path: storagePath,
      mime_type: "application/pdf",
      file_size_bytes: selectedFile.size,
      checksum_sha256: checksum,
      status: "uploaded"
    });

    if (insertError) {
      await supabase.storage.from(DOCUMENT_BUCKET).remove([storagePath]);
      setUploadState({
        status: "error",
        message: insertError.message
      });
      return;
    }

    setSelectedFile(null);
    setFileInputKey((current) => current + 1);
    setDescription("");
    setUploadState({
      status: "success",
      message:
        "Document uploaded instantly. Processing has started; refresh My Documents in a moment."
    });

    void fetch(`/api/documents/${documentId}/parse`, {
      method: "POST",
      keepalive: true
    });
  }

  return (
    <form
      className="mt-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
      onSubmit={handleUpload}
    >
      <label className="block text-sm font-semibold" htmlFor="file">
        PDF file
      </label>
      <input
        accept="application/pdf,.pdf"
        className="mt-2 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm file:mr-4 file:rounded-md file:border-0 file:bg-accent file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
        id="file"
        key={fileInputKey}
        onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
        type="file"
      />

      <label className="mt-5 block text-sm font-semibold" htmlFor="category">
        Category
      </label>
      <select
        className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
        id="category"
        onChange={(event) => setCategory(event.target.value)}
        value={category}
      >
        {categories.map((item) => (
          <option key={item.value} value={item.value}>
            {item.label}
          </option>
        ))}
      </select>

      <label className="mt-5 block text-sm font-semibold" htmlFor="description">
        Description
      </label>
      <textarea
        className="mt-2 min-h-28 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
        id="description"
        onChange={(event) => setDescription(event.target.value)}
        placeholder="Optional context for admins and future search filters"
        value={description}
      />

      <button
        className="mt-6 flex items-center justify-center gap-2 rounded-md bg-accent px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={uploadState.status === "uploading"}
        type="submit"
      >
        {uploadState.status === "uploading" ? (
          <Loader2 aria-hidden="true" className="animate-spin" size={18} />
        ) : (
          <FileUp aria-hidden="true" size={18} />
        )}
        {uploadState.status === "uploading" ? "Uploading to Supabase..." : "Upload PDF"}
      </button>

      {uploadState.message ? (
        <p
          className={`mt-4 rounded-md border px-4 py-3 text-sm ${
            uploadState.status === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-700"
              : "border-red-200 bg-red-50 text-red-700"
          }`}
        >
          {uploadState.message}
        </p>
      ) : null}
    </form>
  );
}

async function validatePdf(file: File): Promise<string | null> {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    return "Only PDF files are supported.";
  }

  if (file.type && file.type !== "application/pdf") {
    return "File must use application/pdf content type.";
  }

  if (file.size === 0) {
    return "Uploaded file is empty.";
  }

  if (file.size > MAX_UPLOAD_BYTES) {
    return "File size exceeds the 10 MB upload limit.";
  }

  const header = new Uint8Array(await file.slice(0, 4).arrayBuffer());
  const looksLikePdf =
    header[0] === 0x25 && header[1] === 0x50 && header[2] === 0x44 && header[3] === 0x46;

  if (!looksLikePdf) {
    return "Uploaded file does not look like a valid PDF.";
  }

  return null;
}

function sanitizeFilename(filename: string): string {
  const cleanName = filename
    .trim()
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^[.-]+|[.-]+$/g, "");

  if (!cleanName) {
    return "document.pdf";
  }

  return cleanName.toLowerCase().endsWith(".pdf") ? cleanName : `${cleanName}.pdf`;
}

async function sha256Hex(file: File): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}
