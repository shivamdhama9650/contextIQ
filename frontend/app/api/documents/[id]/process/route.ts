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

  let backendResponse: Response;

  try {
    backendResponse = await fetch(`${env.apiBaseUrl}/documents/${id}/process`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.access_token}`
      },
      cache: "no-store"
    });
  } catch {
    return NextResponse.json(
      { detail: "Backend is not reachable. Document processing could not start." },
      { status: 503 }
    );
  }

  const body = await backendResponse.json().catch(() => ({
    detail: "Processing could not start"
  }));

  return NextResponse.json(body, { status: backendResponse.status });
}
