-- Phase 7: Store vector embeddings for document chunks (JSON arrays until ChromaDB in Phase 8).

create table if not exists public.chunk_embeddings (
    id uuid primary key default gen_random_uuid(),
    chunk_id uuid not null unique references public.document_chunks(id) on delete cascade,
    document_id uuid not null references public.documents(id) on delete cascade,
    model_name text not null,
    dimensions integer not null check (dimensions > 0),
    embedding jsonb not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_chunk_embeddings_document_id on public.chunk_embeddings(document_id);
create index if not exists idx_chunk_embeddings_chunk_id on public.chunk_embeddings(chunk_id);

alter table public.chunk_embeddings enable row level security;

drop policy if exists "Users can read embeddings for visible documents" on public.chunk_embeddings;
create policy "Users can read embeddings for visible documents"
on public.chunk_embeddings
for select
to authenticated
using (
    exists (
        select 1
        from public.documents d
        where d.id = public.chunk_embeddings.document_id
          and (d.status = 'ready' or d.owner_id = auth.uid() or public.can_manage_category(d.category))
    )
);
