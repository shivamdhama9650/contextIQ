import { after, NextResponse } from "next/server";

import { env } from "@/lib/env";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";

const DOCUMENT_BUCKET = "company-documents";
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(request: Request) {
  const supabase = await createClient();
  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const formData = await request.formData();
  const file = formData.get("file");
  const category = String(formData.get("category") ?? "general");
  const description = String(formData.get("description") ?? "").trim() || null;

  if (!(file instanceof File)) {
    return NextResponse.json({ detail: "Choose a PDF file before uploading." }, { status: 400 });
  }

  const validationError = await validatePdf(file);
  if (validationError) {
    return NextResponse.json({ detail: validationError }, { status: 400 });
  }

  const admin = createAdminClient();
  const documentId = crypto.randomUUID();
  const filename = sanitizeFilename(file.name || "document.pdf");
  const storagePath = `${session.user.id}/${documentId}/${filename}`;
  const arrayBuffer = await file.arrayBuffer();
  const content = new Uint8Array(arrayBuffer);
  const checksum = await sha256Hex(arrayBuffer);
  const title =
    filename
      .replace(/\.pdf$/i, "")
      .replaceAll("-", " ")
      .replaceAll("_", " ")
      .trim() || "Uploaded document";

  const { error: uploadError } = await admin.storage
    .from(DOCUMENT_BUCKET)
    .upload(storagePath, content, {
      contentType: "application/pdf",
      upsert: false
    });

  if (uploadError) {
    return NextResponse.json({ detail: uploadError.message }, { status: 500 });
  }

  const { data, error: insertError } = await admin
    .from("documents")
    .insert({
      id: documentId,
      owner_id: session.user.id,
      title,
      description,
      category,
      storage_bucket: DOCUMENT_BUCKET,
      storage_path: storagePath,
      mime_type: "application/pdf",
      file_size_bytes: file.size,
      checksum_sha256: checksum,
      status: "uploaded"
    })
    .select("*")
    .single();

  if (insertError) {
    await admin.storage.from(DOCUMENT_BUCKET).remove([storagePath]);
    return NextResponse.json({ detail: insertError.message }, { status: 500 });
  }

  after(async () => {
    try {
      const response = await fetch(`${env.apiBaseUrl}/documents/${documentId}/parse`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`
        },
        cache: "no-store"
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        console.error("Automatic document processing failed", {
          documentId,
          status: response.status,
          detail: body?.detail ?? "Unknown backend error"
        });
      }
    } catch (error) {
      console.error("Automatic document processing request failed", {
        documentId,
        error
      });
    }
  });

  return NextResponse.json(
    {
      document: data,
      message: "Document uploaded. Parsing, chunking, embeddings, and indexing have started."
    },
    { status: 201 }
  );
}

async function validatePdf(file: File): Promise<string | null> {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    return "Only PDF files are supported.";
  }

  if (file.type && file.type !== "application/pdf") {
    return "File must use application/pdf content type.";
  }

  if (file.size === 0) {
    return "Uploaded file is empty.";
  }

  if (file.size > MAX_UPLOAD_BYTES) {
    return "File size exceeds the 10 MB upload limit.";
  }

  const header = new Uint8Array(await file.slice(0, 4).arrayBuffer());
  const looksLikePdf =
    header[0] === 0x25 && header[1] === 0x50 && header[2] === 0x44 && header[3] === 0x46;

  if (!looksLikePdf) {
    return "Uploaded file does not look like a valid PDF.";
  }

  return null;
}

function sanitizeFilename(filename: string): string {
  const cleanName = filename
    .trim()
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^[.-]+|[.-]+$/g, "");

  if (!cleanName) {
    return "document.pdf";
  }

  return cleanName.toLowerCase().endsWith(".pdf") ? cleanName : `${cleanName}.pdf`;
}

async function sha256Hex(content: ArrayBuffer): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", content);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}
