import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import Link from "next/link";

interface SourceDetail {
  document_id: string;
  title: string;
  preview: string;
}

export default function SourceDetailPage() {
  const router = useRouter();
  const { document_id } = router.query as { document_id: string };
  const [source, setSource] = useState<SourceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!document_id) return;
    const fetchSource = async () => {
      try {
        const res = await fetch(`/api/source/${document_id}`);
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Failed to load source");
        }
        const data = await res.json();
        setSource(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchSource();
  }, [document_id]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-red-600">{error}</p>
        <Link href="/chat" className="ml-4 text-blue-600 underline">
          Back to chat
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">{source?.title}</h1>
      <p className="whitespace-pre-wrap text-slate-700 mb-6">{source?.preview}</p>
      <Link href="/chat" className="text-blue-600 underline">
        ← Back to chat
      </Link>
    </div>
  );
}
