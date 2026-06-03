import { NextResponse } from "next/server";

import { env } from "@/lib/env";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const formData = await request.formData();

  let backendResponse: Response;

  try {
    backendResponse = await fetch(`${env.apiBaseUrl}/documents/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.access_token}`
      },
      body: formData,
      cache: "no-store"
    });
  } catch {
    return NextResponse.json(
      {
        detail:
          "Backend is not reachable. Start the API with: uvicorn app.main:app --reload --port 8000"
      },
      { status: 503 }
    );
  }

  const body = await backendResponse.json().catch(() => ({
    detail: "Upload failed"
  }));

  return NextResponse.json(body, { status: backendResponse.status });
}
