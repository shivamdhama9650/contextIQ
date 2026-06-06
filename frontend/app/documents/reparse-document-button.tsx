"use client";

import { Loader2, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { formatApiError } from "@/lib/api/errors";

type Props = {
  documentId: string;
  label?: string;
};

export function ReparseDocumentButton({ documentId, label = "Parse PDF" }: Props) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);

  async function handleParse() {
    setIsLoading(true);
    setMessage(null);
    setIsError(false);

    try {
      const response = await fetch(`/api/documents/${documentId}/process`, {
        method: "POST"
      });
      const body = await response.json().catch(() => null);

      if (!response.ok) {
        setMessage(formatApiError(body, "Parsing failed."));
        setIsError(true);
        setIsLoading(false);
        return;
      }

      setMessage(body?.message ?? "Processing started.");
      setIsError(false);
      router.refresh();
    } catch {
      setMessage("Parsing request failed. Is the backend running on port 8000?");
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div>
      <button
        className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={isLoading}
        onClick={handleParse}
        type="button"
      >
        {isLoading ? (
          <Loader2 aria-hidden="true" className="animate-spin" size={16} />
        ) : (
          <RefreshCw aria-hidden="true" size={16} />
        )}
        {isLoading ? "Parsing..." : label}
      </button>
      {message ? (
        <p
          className={`mt-3 rounded-md border px-3 py-2 text-sm ${
            isError
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-700"
          }`}
        >
          {message}
        </p>
      ) : null}
    </div>
  );
}
