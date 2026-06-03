import { createClient as createSupabaseClient } from "@supabase/supabase-js";

import { getSupabaseServerConfig } from "@/lib/env";

export function createAdminClient() {
  const { supabaseUrl, serviceRoleKey } = getSupabaseServerConfig();

  return createSupabaseClient(supabaseUrl, serviceRoleKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  });
}
