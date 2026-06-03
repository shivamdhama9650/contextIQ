"""Quick Supabase connectivity check. Run from backend/: python scripts/check_supabase.py"""

import httpx
from supabase import create_client

from app.core.config import settings


def main() -> None:
    print("URL configured:", bool(settings.supabase_url))
    print("Anon key configured:", bool(settings.supabase_anon_key))
    print("Service role configured:", bool(settings.supabase_service_role_key))

    if not settings.supabase_url or not settings.supabase_service_role_key:
        print("FAIL: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in backend/.env")
        return

    client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    try:
        client.table("profiles").select("id", count="exact").limit(1).execute()
        print("DB query: OK (profiles table reachable)")
    except Exception as exc:
        print("DB query: FAIL -", exc)

    try:
        buckets = client.storage.list_buckets()
        names = [b.name for b in buckets]
        print("Storage: OK, buckets:", names)
        if "company-documents" in names:
            print("company-documents bucket: FOUND")
        else:
            print(
                "company-documents bucket: MISSING - run "
                "supabase/migrations/0002_document_storage_bucket.sql"
            )
    except Exception as exc:
        print("Storage: FAIL -", exc)

    try:
        jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        response = httpx.get(jwks_url, timeout=10)
        print("Auth JWKS:", response.status_code, "(200 = OK for login token verification)")
    except Exception as exc:
        print("Auth JWKS: FAIL -", exc)


if __name__ == "__main__":
    main()
