-- Allow authenticated browser uploads directly into each user's own storage prefix.
-- Required for instant uploads that bypass the Render backend.

drop policy if exists "Users can upload documents to their own folder" on storage.objects;
create policy "Users can upload documents to their own folder"
on storage.objects
for insert
to authenticated
with check (
    bucket_id = 'company-documents'
    and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users can read documents from their own folder" on storage.objects;
create policy "Users can read documents from their own folder"
on storage.objects
for select
to authenticated
using (
    bucket_id = 'company-documents'
    and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users can delete documents from their own folder" on storage.objects;
create policy "Users can delete documents from their own folder"
on storage.objects
for delete
to authenticated
using (
    bucket_id = 'company-documents'
    and (storage.foldername(name))[1] = auth.uid()::text
);
