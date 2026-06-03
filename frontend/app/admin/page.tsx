import { FileText, Shield, Users } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import {
  appRoles,
  fetchAdminDocuments,
  fetchAdminProfiles,
  fetchCurrentProfile,
  formatRole,
  type ProfileRecord
} from "@/lib/api/admin";
import {
  formatDocumentStatus,
  formatFileSize,
  statusBadgeClass,
  type DocumentRecord
} from "@/lib/api/documents";
import { createClient } from "@/lib/supabase/server";

import { updateUserRole } from "./actions";

export default async function AdminDashboardPage() {
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
  let profiles: ProfileRecord[] = [];
  let documents: DocumentRecord[] = [];
  let loadError: string | null = null;

  try {
    currentProfile = await fetchCurrentProfile(session.access_token);

    if (currentProfile.role === "admin") {
      [profiles, documents] = await Promise.all([
        fetchAdminProfiles(session.access_token),
        fetchAdminDocuments(session.access_token)
      ]);
    }
  } catch (error) {
    loadError =
      error instanceof Error
        ? error.message
        : "Admin dashboard could not be loaded.";
  }

  const isAdmin = currentProfile?.role === "admin";

  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-accent">
              Admin console
            </p>
            <h1 className="mt-2 text-3xl font-semibold">Admin dashboard</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              Manage user roles and inspect document ingestion from one protected
              operational view.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-slate-50"
              href="/analytics"
            >
              Analytics
            </Link>
            <Link
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold transition hover:bg-slate-50"
              href="/dashboard"
            >
              Back to dashboard
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
                  Set your Supabase profiles role to admin to use this dashboard.
                </p>
              </div>
            </div>
          </div>
        ) : null}

        {!loadError && isAdmin ? (
          <>
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <MetricCard label="Users" value={profiles.length} icon="users" />
              <MetricCard label="Documents" value={documents.length} icon="files" />
              <MetricCard
                label="Ready documents"
                value={documents.filter((document) => document.status === "ready").length}
                icon="shield"
              />
            </div>

            <section className="mt-8">
              <div className="mb-3 flex items-center gap-2">
                <Users aria-hidden="true" className="text-accent" size={20} />
                <h2 className="text-xl font-semibold">Users and roles</h2>
              </div>
              <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-4 py-3">User</th>
                      <th className="px-4 py-3">Role</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Change role</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {profiles.map((profile) => (
                      <tr key={profile.id}>
                        <td className="px-4 py-4">
                          <p className="font-medium">{profile.full_name ?? profile.email}</p>
                          <p className="mt-1 text-xs text-slate-500">{profile.email}</p>
                        </td>
                        <td className="px-4 py-4 capitalize text-slate-700">
                          {formatRole(profile.role)}
                        </td>
                        <td className="px-4 py-4">
                          {profile.is_active ? "Active" : "Inactive"}
                        </td>
                        <td className="px-4 py-4">
                          <form action={updateUserRole} className="flex gap-2">
                            <input name="user_id" type="hidden" value={profile.id} />
                            <select
                              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
                              defaultValue={profile.role}
                              name="role"
                            >
                              {appRoles.map((role) => (
                                <option key={role} value={role}>
                                  {formatRole(role)}
                                </option>
                              ))}
                            </select>
                            <button
                              className="rounded-md bg-accent px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                              type="submit"
                            >
                              Save
                            </button>
                          </form>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="mt-8">
              <div className="mb-3 flex items-center gap-2">
                <FileText aria-hidden="true" className="text-accent" size={20} />
                <h2 className="text-xl font-semibold">Document operations</h2>
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
                    {documents.map((document) => (
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
                    ))}
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
  label,
  value,
  icon
}: {
  label: string;
  value: number;
  icon: "users" | "files" | "shield";
}) {
  const Icon = icon === "users" ? Users : icon === "files" ? FileText : Shield;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-600">{label}</p>
        <Icon aria-hidden="true" className="text-accent" size={20} />
      </div>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
    </div>
  );
}
