import {
  Activity,
  AlertTriangle,
  BarChart3,
  Database,
  FileText,
  HardDrive,
  Shield,
  Users
} from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import {
  fetchAdminAnalytics,
  fetchCurrentProfile,
  formatRole,
  type AnalyticsBreakdownItem,
  type AnalyticsOverview,
  type ProfileRecord
} from "@/lib/api/admin";
import {
  formatDocumentStatus,
  formatFileSize,
  statusBadgeClass
} from "@/lib/api/documents";
import { createClient } from "@/lib/supabase/server";

export default async function AnalyticsDashboardPage() {
  const supabase = await createClient();
  const {
    data: { user }
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    redirect("/auth/login");
  }

  let currentProfile: ProfileRecord | null = null;
  let analytics: AnalyticsOverview | null = null;
  let loadError: string | null = null;

  try {
    currentProfile = await fetchCurrentProfile(session.access_token);

    if (currentProfile.role === "admin") {
      analytics = await fetchAdminAnalytics(session.access_token);
    }
  } catch (error) {
    loadError =
      error instanceof Error
        ? error.message
        : "Analytics dashboard could not be loaded.";
  }

  const isAdmin = currentProfile?.role === "admin";

  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-accent">
              Platform analytics
            </p>
            <h1 className="mt-2 text-3xl font-semibold">Analytics dashboard</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              Track adoption, document ingestion health, storage growth, and RAG
              readiness from an admin-only operational view.
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
              href="/dashboard"
            >
              Dashboard
            </Link>
          </div>
        </div>

        {loadError ? (
          <p className="mt-8 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {loadError}
          </p>
        ) : null}

        {!loadError && !isAdmin ? (
          <div className="mt-8 rounded-lg border border-amber-200 bg-amber-50 p-6">
            <div className="flex items-start gap-3">
              <Shield aria-hidden="true" className="text-amber-700" size={22} />
              <div>
                <h2 className="text-lg font-semibold text-amber-900">
                  Admin role required
                </h2>
                <p className="mt-2 text-sm leading-6 text-amber-800">
                  Your current role is {formatRole(currentProfile?.role ?? "unknown")}.
                  Set your Supabase profiles role to admin to view platform analytics.
                </p>
              </div>
            </div>
          </div>
        ) : null}

        {!loadError && isAdmin && analytics ? (
          <>
            <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard
                icon="users"
                label="Active users"
                tone="blue"
                value={`${analytics.active_users}/${analytics.total_users}`}
              />
              <MetricCard
                icon="files"
                label="Ready documents"
                tone="green"
                value={`${analytics.ready_documents}/${analytics.total_documents}`}
              />
              <MetricCard
                icon="database"
                label="Chunks indexed"
                tone="violet"
                value={analytics.total_chunks.toLocaleString()}
              />
              <MetricCard
                icon="storage"
                label="Storage used"
                tone="amber"
                value={formatFileSize(analytics.total_storage_bytes)}
              />
            </div>

            <section className="mt-8 grid gap-6 lg:grid-cols-[1fr_0.9fr]">
              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold">Ingestion health</h2>
                    <p className="mt-1 text-sm text-slate-600">
                      Shows whether uploaded documents are ready for retrieval.
                    </p>
                  </div>
                  <div className="rounded-md bg-emerald-50 p-2 text-emerald-700">
                    <Activity aria-hidden="true" size={22} />
                  </div>
                </div>

                <div className="mt-6">
                  <div className="flex items-end justify-between gap-4">
                    <p className="text-sm font-medium text-slate-600">
                      Readiness rate
                    </p>
                    <p className="text-3xl font-semibold">
                      {analytics.readiness_rate}%
                    </p>
                  </div>
                  <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${analytics.readiness_rate}%` }}
                    />
                  </div>
                </div>

                <div className="mt-6 grid gap-3 sm:grid-cols-3">
                  <HealthPill
                    label="Failed"
                    tone="red"
                    value={analytics.failed_documents}
                  />
                  <HealthPill
                    label="Processing"
                    tone="amber"
                    value={analytics.processing_documents}
                  />
                  <HealthPill
                    label="Embeddings"
                    tone="blue"
                    value={analytics.total_embeddings}
                  />
                </div>
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-2">
                  <BarChart3 aria-hidden="true" className="text-accent" size={20} />
                  <h2 className="text-xl font-semibold">Document status</h2>
                </div>
                <BreakdownList items={analytics.status_breakdown} />
              </div>
            </section>

            <section className="mt-8 grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-2">
                  <FileText aria-hidden="true" className="text-accent" size={20} />
                  <h2 className="text-xl font-semibold">Categories</h2>
                </div>
                <BreakdownList items={analytics.category_breakdown} />
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-2">
                  <Users aria-hidden="true" className="text-accent" size={20} />
                  <h2 className="text-xl font-semibold">Roles</h2>
                </div>
                <BreakdownList items={analytics.role_breakdown} formatter={formatRole} />
              </div>
            </section>

            <section className="mt-8">
              <div className="mb-3 flex items-center gap-2">
                <AlertTriangle aria-hidden="true" className="text-accent" size={20} />
                <h2 className="text-xl font-semibold">Recent document activity</h2>
              </div>
              <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-4 py-3">Title</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Size</th>
                      <th className="px-4 py-3">Uploaded</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {analytics.recent_documents.length > 0 ? (
                      analytics.recent_documents.map((document) => (
                        <tr key={document.id}>
                          <td className="px-4 py-4 font-medium">{document.title}</td>
                          <td className="px-4 py-4 capitalize text-slate-600">
                            {document.category}
                          </td>
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
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td className="px-4 py-6 text-slate-600" colSpan={5}>
                          No documents have been uploaded yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        ) : null}
      </section>
    </main>
  );
}

function MetricCard({
  icon,
  label,
  tone,
  value
}: {
  icon: "users" | "files" | "database" | "storage";
  label: string;
  tone: "blue" | "green" | "violet" | "amber";
  value: string;
}) {
  const Icon =
    icon === "users"
      ? Users
      : icon === "files"
        ? FileText
        : icon === "database"
          ? Database
          : HardDrive;
  const toneClass = {
    amber: "bg-amber-50 text-amber-700",
    blue: "bg-blue-50 text-blue-700",
    green: "bg-emerald-50 text-emerald-700",
    violet: "bg-violet-50 text-violet-700"
  }[tone];

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-600">{label}</p>
        <div className={`rounded-md p-2 ${toneClass}`}>
          <Icon aria-hidden="true" size={20} />
        </div>
      </div>
      <p className="mt-4 text-3xl font-semibold">{value}</p>
    </div>
  );
}

function HealthPill({
  label,
  tone,
  value
}: {
  label: string;
  tone: "red" | "amber" | "blue";
  value: number;
}) {
  const toneClass = {
    amber: "border-amber-200 bg-amber-50 text-amber-800",
    blue: "border-blue-200 bg-blue-50 text-blue-800",
    red: "border-red-200 bg-red-50 text-red-800"
  }[tone];

  return (
    <div className={`rounded-md border px-4 py-3 ${toneClass}`}>
      <p className="text-xs font-semibold uppercase tracking-wide">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value.toLocaleString()}</p>
    </div>
  );
}

function BreakdownList({
  formatter = (value: string) => value,
  items
}: {
  formatter?: (value: string) => string;
  items: AnalyticsBreakdownItem[];
}) {
  if (items.length === 0) {
    return <p className="mt-5 text-sm text-slate-600">No data available yet.</p>;
  }

  return (
    <div className="mt-5 space-y-4">
      {items.map((item) => (
        <div key={item.label}>
          <div className="flex items-center justify-between gap-4 text-sm">
            <p className="font-medium capitalize">{formatter(item.label)}</p>
            <p className="text-slate-600">
              {item.count.toLocaleString()} - {item.percentage}%
            </p>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-blue-500"
              style={{ width: `${item.percentage}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
