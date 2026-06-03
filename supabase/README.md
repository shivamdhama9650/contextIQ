# Supabase

This folder stores database migrations and Supabase-specific setup notes.

## Apply Migrations

Use one of these options.

### Option 1: Supabase SQL Editor

1. Open Supabase Dashboard.
2. Go to SQL Editor.
3. Open `migrations/0001_initial_schema.sql`.
4. Paste the full SQL into the editor.
5. Click Run.
6. Open `migrations/0002_document_storage_bucket.sql`.
7. Paste the full SQL into the editor.
8. Click Run.

### Option 2: Supabase CLI

The CLI will be added as an official workflow in a later phase. When installed and linked, this migration can be applied with:

```powershell
supabase db push
```

## Important Security Note

The schema enables row-level security on all application tables. The document bucket is private. The backend service-role key can bypass RLS and write to private storage, so it must never be exposed to the frontend.
