import { NextResponse } from "next/server";

import { env } from "@/lib/env";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
  const supabase = await createClient();
  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  let backendResponse: Response;

  try {
    backendResponse = await fetch(`${env.apiBaseUrl}/documents`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`
      },
      cache: "no-store",
      signal: AbortSignal.timeout(15000)
    });
  } catch {
    return NextResponse.json(
      {
        detail:
          "Document service is waking up or temporarily unavailable. Please retry in a moment."
      },
      { status: 503 }
    );
  }

  const body = await backendResponse.json().catch(() => ({
    detail: "Could not load documents"
  }));

  return NextResponse.json(body, { status: backendResponse.status });
}
