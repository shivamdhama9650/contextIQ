"use client";

import { FileUp, Loader2 } from "lucide-react";
import { useState } from "react";

import { formatApiError } from "@/lib/api/errors";
import { createClient } from "@/lib/supabase/browser";

const categories = [
  { label: "General", value: "general" },
  { label: "HR", value: "hr" },
  { label: "DevOps", value: "devops" },
  { label: "Security", value: "security" },
  { label: "Finance", value: "finance" },
  { label: "Technical", value: "technical" }
];

const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

type UploadState = {
  status: "idle" | "uploading" | "processing" | "success" | "error";
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

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("category", category);

    if (description.trim()) {
      formData.append("description", description.trim());
    }

    const response = await fetch("/api/documents/upload", {
      method: "POST",
      body: formData
    });
    const responseBody = await response.json().catch(() => null);

    if (!response.ok) {
      setUploadState({
        status: "error",
        message: formatApiError(responseBody, "Upload failed.")
      });
      return;
    }

    const documentId = responseBody?.document?.id;

    setSelectedFile(null);
    setFileInputKey((current) => current + 1);
    setDescription("");
    setUploadState({
      status: "processing",
      message:
        responseBody?.message ??
        "Document uploaded. Parsing, chunking, embeddings, and indexing have started."
    });

    if (documentId) {
      await waitForDocumentProcessing(documentId, setUploadState);
    }
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
        disabled={uploadState.status === "uploading" || uploadState.status === "processing"}
        type="submit"
      >
        {uploadState.status === "uploading" || uploadState.status === "processing" ? (
          <Loader2 aria-hidden="true" className="animate-spin" size={18} />
        ) : (
          <FileUp aria-hidden="true" size={18} />
        )}
        {buttonLabel(uploadState.status)}
      </button>

      {uploadState.message ? (
        <p
          className={`mt-4 rounded-md border px-4 py-3 text-sm ${
            uploadState.status === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-700"
              : uploadState.status === "processing"
                ? "border-blue-200 bg-blue-50 text-blue-800"
              : "border-red-200 bg-red-50 text-red-700"
          }`}
        >
          {uploadState.message}
        </p>
      ) : null}
    </form>
  );
}

function buttonLabel(status: UploadState["status"]): string {
  if (status === "uploading") {
    return "Uploading to Supabase...";
  }

  if (status === "processing") {
    return "Processing document...";
  }

  return "Upload PDF";
}

async function waitForDocumentProcessing(
  documentId: string,
  setUploadState: React.Dispatch<React.SetStateAction<UploadState>>
) {
  const supabase = createClient();
  const attempts = 60;
  const delayMs = 2000;

  for (let attempt = 0; attempt < attempts; attempt += 1) {
    await delay(delayMs);

    const { data, error } = await supabase
      .from("documents")
      .select("status, error_message")
      .eq("id", documentId)
      .maybeSingle();

    if (error) {
      setUploadState({
        status: "error",
        message: formatApiError({ detail: error.message }, "Could not check processing status.")
      });
      return;
    }

    if (!data) {
      setUploadState({
        status: "error",
        message: "Uploaded document could not be found."
      });
      return;
    }

    if (data.status === "ready") {
      setUploadState({
        status: "success",
        message: "Document is ready. It has been parsed, chunked, embedded, and indexed for chat."
      });
      return;
    }

    if (data.status === "failed") {
      setUploadState({
        status: "error",
        message:
          data.error_message ??
          "Document processing failed. The PDF may be scanned or image-only."
      });
      return;
    }

    setUploadState({
      status: "processing",
      message:
        data.status === "processing"
          ? "Processing is running: extracting text, chunking, embedding, and indexing."
          : "Document uploaded. Waiting for the processing worker to start."
    });
  }

  setUploadState({
    status: "processing",
    message:
      "Processing is still running in the background. You can open My Documents and refresh status."
  });
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
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
