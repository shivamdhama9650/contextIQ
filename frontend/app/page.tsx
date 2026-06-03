import {
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  Database,
  FileSearch,
  FileText,
  LockKeyhole,
  ShieldCheck,
  Upload
} from "lucide-react";
import Link from "next/link";

const workflow = [
  {
    icon: Upload,
    title: "Upload trusted PDFs",
    description: "Add HR, security, finance, SOP, deployment, and policy documents."
  },
  {
    icon: Database,
    title: "Index company knowledge",
    description: "Parse, chunk, embed, and store searchable vectors for grounded retrieval."
  },
  {
    icon: Bot,
    title: "Ask with confidence",
    description: "Get answers only from indexed documents, with sources available for review."
  }
];

const highlights = [
  "Supabase authentication and role-based access",
  "Groq/Gemini-ready RAG answer generation",
  "ChromaDB vector search with SentenceTransformers",
  "Admin analytics for ingestion and document health"
];

const documentTypes = ["HR Policies", "Security SOPs", "Finance Docs", "Deployment Guides"];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-surface text-ink">
      <section className="mx-auto grid min-h-screen w-full max-w-6xl gap-10 px-6 py-10 lg:grid-cols-[1fr_0.9fr] lg:items-center">
        <div>
          <p className="inline-flex rounded-md bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-accent">
            Secure company knowledge
          </p>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight sm:text-5xl">
            Ask questions across company documents without leaving the source of truth.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-700 sm:text-lg">
            Enterprise Knowledge Assistant helps employees upload approved PDFs,
            search internal knowledge, and receive grounded answers with document
            context instead of unsupported guesses.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              className="inline-flex items-center gap-2 rounded-md bg-accent px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
              href="/auth/login"
            >
              Continue to login
              <ArrowRight aria-hidden="true" size={16} />
            </Link>
            <Link
              className="rounded-md border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:bg-slate-50"
              href="/dashboard"
            >
              Open dashboard
            </Link>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            {highlights.map((item) => (
              <div className="flex items-start gap-2 text-sm text-slate-700" key={item}>
                <CheckCircle2
                  aria-hidden="true"
                  className="mt-0.5 shrink-0 text-emerald-600"
                  size={16}
                />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white shadow-xl">
          <div className="border-b border-slate-100 px-5 py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold">Knowledge operations</p>
                <p className="mt-1 text-xs text-slate-500">
                  Documents, retrieval, and access controls in one workspace.
                </p>
              </div>
              <div className="rounded-md bg-emerald-50 p-2 text-emerald-700">
                <ShieldCheck aria-hidden="true" size={20} />
              </div>
            </div>
          </div>

          <div className="grid gap-4 p-5">
            <div className="grid grid-cols-2 gap-3">
              <PreviewMetric icon={FileText} label="Indexed docs" value="5" />
              <PreviewMetric icon={FileSearch} label="Retrieval ready" value="100%" />
              <PreviewMetric icon={LockKeyhole} label="RBAC roles" value="6" />
              <PreviewMetric icon={BarChart3} label="Analytics" value="Live" />
            </div>

            <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Example answer
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-700">
                "Password requirements are answered from the Security Policy,
                with the matching source page attached for verification."
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {documentTypes.map((type) => (
                  <span
                    className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600"
                    key={type}
                  >
                    {type}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-200 bg-white px-6 py-10">
        <div className="mx-auto grid max-w-6xl gap-4 md:grid-cols-3">
          {workflow.map((item) => (
            <article className="rounded-lg border border-slate-200 p-5" key={item.title}>
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-blue-50 text-accent">
                <item.icon aria-hidden="true" size={20} />
              </div>
              <h2 className="mt-4 text-base font-semibold">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function PreviewMetric({
  icon: Icon,
  label,
  value
}: {
  icon: typeof FileText;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-slate-200 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-medium text-slate-500">{label}</p>
        <Icon aria-hidden="true" className="text-accent" size={16} />
      </div>
      <p className="mt-3 text-2xl font-semibold">{value}</p>
    </div>
  );
}
