"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { type AppRole, appRoles, updateProfileRole } from "@/lib/api/admin";
import { createClient } from "@/lib/supabase/server";

export async function updateUserRole(formData: FormData) {
  const userId = String(formData.get("user_id") ?? "");
  const role = String(formData.get("role") ?? "") as AppRole;

  if (!userId || !appRoles.includes(role)) {
    throw new Error("Invalid role update request.");
  }

  const supabase = await createClient();
  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    redirect("/auth/login");
  }

  await updateProfileRole(session.access_token, userId, role);
  revalidatePath("/admin");
}

