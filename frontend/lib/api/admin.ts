import { formatApiError } from "@/lib/api/errors";
import { type DocumentRecord } from "@/lib/api/documents";
import { env } from "@/lib/env";

export const appRoles = [
  "employee",
  "hr_admin",
  "devops_admin",
  "security_admin",
  "finance_admin",
  "admin"
] as const;

export type AppRole = (typeof appRoles)[number];

export type ProfileRecord = {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: AppRole;
  department: string | null;
  job_title: string | null;
  is_active: boolean;
};

export type AnalyticsBreakdownItem = {
  label: string;
  count: number;
  percentage: number;
};

export type AnalyticsOverview = {
  total_users: number;
  active_users: number;
  inactive_users: number;
  total_documents: number;
  ready_documents: number;
  failed_documents: number;
  processing_documents: number;
  uploaded_documents: number;
  archived_documents: number;
  total_storage_bytes: number;
  total_chunks: number;
  total_embeddings: number;
  readiness_rate: number;
  category_breakdown: AnalyticsBreakdownItem[];
  status_breakdown: AnalyticsBreakdownItem[];
  role_breakdown: AnalyticsBreakdownItem[];
  recent_documents: DocumentRecord[];
};

async function adminFetch<T>(
  path: string,
  accessToken: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(formatApiError(body, `Request failed (${response.status})`));
  }

  return body as T;
}

export async function fetchCurrentProfile(accessToken: string): Promise<ProfileRecord> {
  return adminFetch<ProfileRecord>("/auth/me", accessToken);
}

export async function fetchAdminProfiles(accessToken: string): Promise<ProfileRecord[]> {
  return adminFetch<ProfileRecord[]>("/auth/profiles", accessToken);
}

export async function fetchAdminDocuments(accessToken: string): Promise<DocumentRecord[]> {
  return adminFetch<DocumentRecord[]>("/documents/admin/all", accessToken);
}

export async function fetchAdminAnalytics(
  accessToken: string
): Promise<AnalyticsOverview> {
  return adminFetch<AnalyticsOverview>("/analytics/admin/overview", accessToken);
}

export async function updateProfileRole(
  accessToken: string,
  userId: string,
  role: AppRole
): Promise<ProfileRecord> {
  return adminFetch<ProfileRecord>(`/auth/profiles/${userId}/role`, accessToken, {
    method: "PATCH",
    body: JSON.stringify({ role })
  });
}

export function formatRole(role: string): string {
  return role.replaceAll("_", " ");
}
