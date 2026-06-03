import { NextResponse } from "next/server";

import { env } from "@/lib/env";
import { createClient } from "@/lib/supabase/server";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(_request: Request, context: RouteContext) {
  const { id } = await context.params;
  const supabase = await createClient();
  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  try {
    const backendResponse = await fetch(`${env.apiBaseUrl}/documents/${id}/embed`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.access_token}`
      },
      cache: "no-store"
    });

    const body = await backendResponse.json().catch(() => ({
      detail: "Embedding failed"
    }));

    return NextResponse.json(body, { status: backendResponse.status });
  } catch {
    return NextResponse.json(
      { detail: "Backend is not reachable on port 8000." },
      { status: 503 }
    );
  }
}
