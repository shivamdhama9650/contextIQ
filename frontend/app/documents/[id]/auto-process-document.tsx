"use client";

import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

type Props = {
  documentId: string;
  status: string;
};

export function AutoProcessDocument({ documentId, status }: Props) {
  const router = useRouter();
  const [message, setMessage] = useState(
    status === "processing"
      ? "Processing is running automatically."
      : "Processing is starting automatically."
  );

  useEffect(() => {
    let isMounted = true;
    let refreshTimer: number | undefined;

    async function startProcessing() {
      if (status === "uploaded") {
        try {
          const response = await fetch(`/api/documents/${documentId}/process`, {
            method: "POST"
          });
          if (!response.ok && isMounted) {
            setMessage("Processing could not start yet. Refresh this page in a moment.");
          }
        } catch {
          if (isMounted) {
            setMessage("Processing could not start yet. Refresh this page in a moment.");
          }
        }
      }

      refreshTimer = window.setInterval(() => {
        router.refresh();
      }, 2500);
    }

    void startProcessing();

    return () => {
      isMounted = false;
      if (refreshTimer) {
        window.clearInterval(refreshTimer);
      }
    };
  }, [documentId, router, status]);

  return (
    <div className="mt-6 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
      <div className="flex items-center gap-2">
        <Loader2 aria-hidden="true" className="animate-spin" size={16} />
        <span>{message}</span>
      </div>
      <p className="mt-2 text-blue-700">
        The document will become available in chat as soon as parsing, chunking, embeddings,
        and indexing finish.
      </p>
    </div>
  );
}
