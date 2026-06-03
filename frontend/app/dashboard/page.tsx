import {
  ArrowRight,
  BarChart3,
  Bot,
  Database,
  FileSearch,
  FileText,
  LockKeyhole,
  Search,
  ShieldCheck,
  Upload,
  Users
} from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { createClient } from "@/lib/supabase/server";

import { signOut } from "./actions";

const quickActions = [
  {
    description: "Ask policy and process questions grounded in indexed documents.",
    href: "/chat",
    icon: Bot,
    label: "Chat with assistant",
    primary: true
  },
  {
    description: "Find relevant chunks before asking the assistant for a final answer.",
    href: "/search",
    icon: Search,
    label: "Search knowledge"
  },
  {
    description: "Upload PDFs and monitor parsing, embedding, and vector status.",
    href: "/documents/upload",
    icon: Upload,
    label: "Upload document"
  },
  {
    description: "Review your uploaded files, parsed pages, chunks, and embeddings.",
    href: "/documents",
    icon: FileText,
    label: "My documents"
  }
];

const workflow = [
  {
    description: "Company PDFs are stored securely and tied to the authenticated user.",
    icon: Upload,
    title: "Upload"
  },
  {
    description: "The backend extracts page text, builds clean chunks, and creates embeddings.",
    icon: Database,
    title: "Process"
  },
  {
    description: "ChromaDB retrieves the most relevant chunks for each question.",
    icon: FileSearch,
    title: "Retrieve"
  },
  {
    description: "Groq or Gemini answers only from retrieved context and returns sources.",
    icon: Bot,
    title: "Answer"
  }
];

const sampleQuestions = [
  "How do I apply for leave?",
  "What are the password requirements?",
  "What is our deployment process?",
  "How do I submit reimbursement requests?"
];

const trustSignals = [
  {
    icon: ShieldCheck,
    label: "Grounded answers",
    value: "Document-only"
  },
  {
    icon: LockKeyhole,
    label: "Access control",
    value: "Role-based"
  },
  {
    icon: Database,
    label: "Retrieval index",
    value: "ChromaDB"
  }
];

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-accent">
              Enterprise knowledge workspace
            </p>
            <h1 className="mt-2 text-3xl font-semibold">Knowledge Dashboard</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              You are signed in as {user.email ?? "a verified company user"}.
              Choose a workflow below to upload documents, inspect retrieval, or
              ask the assistant a grounded question.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-slate-50"
              href="/admin"
            >
              Admin
            </Link>
            <Link
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-slate-50"
              href="/analytics"
            >
              Analytics
            </Link>
            <form action={signOut}>
              <button
                className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-slate-50"
                type="submit"
              >
                Sign out
              </button>
            </form>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {trustSignals.map((signal) => (
            <StatusCard
              icon={signal.icon}
              key={signal.label}
              label={signal.label}
              value={signal.value}
            />
          ))}
        </div>

        <section className="mt-8 grid gap-4 lg:grid-cols-4">
          {quickActions.map((action) => (
            <Link
              className={`rounded-lg border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${
                action.primary
                  ? "border-blue-200 bg-blue-600 text-white"
                  : "border-slate-200 bg-white text-ink"
              }`}
              href={action.href}
              key={action.href}
            >
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-md ${
                  action.primary ? "bg-white/15 text-white" : "bg-blue-50 text-accent"
                }`}
              >
                <action.icon aria-hidden="true" size={20} />
              </div>
              <div className="mt-4 flex items-start justify-between gap-3">
                <h2 className="text-base font-semibold">{action.label}</h2>
                <ArrowRight aria-hidden="true" className="shrink-0" size={16} />
              </div>
              <p
                className={`mt-2 text-sm leading-6 ${
                  action.primary ? "text-blue-50" : "text-slate-600"
                }`}
              >
                {action.description}
              </p>
            </Link>
          ))}
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1fr_0.85fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold">How answers are produced</h2>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  The assistant follows a retrieval-first workflow so every answer
                  can be traced back to company documents.
                </p>
              </div>
              <div className="rounded-md bg-emerald-50 p-2 text-emerald-700">
                <ShieldCheck aria-hidden="true" size={22} />
              </div>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              {workflow.map((step) => (
                <article className="rounded-md border border-slate-200 p-4" key={step.title}>
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-md bg-slate-100 text-slate-700">
                      <step.icon aria-hidden="true" size={18} />
                    </div>
                    <h3 className="font-semibold">{step.title}</h3>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    {step.description}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <Bot aria-hidden="true" className="text-accent" size={20} />
              <h2 className="text-xl font-semibold">Try asking</h2>
            </div>
            <div className="mt-5 space-y-3">
              {sampleQuestions.map((question) => (
                <Link
                  className="block rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                  href={`/chat?question=${encodeURIComponent(question)}`}
                  key={question}
                >
                  {question}
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <Users aria-hidden="true" className="text-accent" size={20} />
              <h2 className="text-lg font-semibold">Admin operations</h2>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Admins can manage user roles, inspect ingestion state, and rebuild
              document indexes when the vector store needs repair.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold transition hover:bg-slate-50"
                href="/admin"
              >
                Manage roles
              </Link>
              <Link
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold transition hover:bg-slate-50"
                href="/analytics"
              >
                View analytics
              </Link>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <BarChart3 aria-hidden="true" className="text-accent" size={20} />
              <h2 className="text-lg font-semibold">Deployment readiness</h2>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              The application is ready for separate frontend and backend hosting:
              Vercel for Next.js, Render for FastAPI, and Supabase for auth,
              database, and storage.
            </p>
          </div>
        </section>
      </section>
    </main>
  );
}

function StatusCard({
  icon: Icon,
  label,
  value
}: {
  icon: typeof ShieldCheck;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-600">{label}</p>
          <p className="mt-2 text-2xl font-semibold">{value}</p>
        </div>
        <div className="rounded-md bg-blue-50 p-2 text-accent">
          <Icon aria-hidden="true" size={20} />
        </div>
      </div>
    </div>
  );
}
