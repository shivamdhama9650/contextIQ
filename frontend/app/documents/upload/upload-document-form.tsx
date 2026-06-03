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

type UploadState = {
  status: "idle" | "uploading" | "success" | "error";
  message: string | null;
};

export function UploadDocumentForm() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
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

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("category", category);

    if (description.trim()) {
      formData.append("description", description.trim());
    }

    let response: Response;

    try {
      // Same-origin proxy avoids browser CORS issues with localhost vs 127.0.0.1
      response = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData
      });
    } catch {
      setUploadState({
        status: "error",
        message:
          "Upload request failed. Make sure the frontend and backend are both running."
      });
      return;
    }

    const responseBody = await response.json().catch(() => null);

    if (!response.ok) {
      setUploadState({
        status: "error",
        message: formatApiError(responseBody, "Upload failed.")
      });
      return;
    }

    setSelectedFile(null);
    setDescription("");
    setUploadState({
      status: "success",
      message: responseBody?.message ?? "Document uploaded successfully."
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
        {uploadState.status === "uploading" ? "Uploading..." : "Upload PDF"}
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

