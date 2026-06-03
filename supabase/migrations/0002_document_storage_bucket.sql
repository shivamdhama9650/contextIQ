-- Phase 4: Private storage bucket for uploaded company documents.
-- The backend uploads with the service-role key. Frontend users never write
-- directly to this bucket in this phase.

insert into storage.buckets (
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types
)
values (
    'company-documents',
    'company-documents',
    false,
    10485760,
    array['application/pdf']
)
on conflict (id) do update set
    public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

