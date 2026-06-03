-- Phase 3: Initial database schema for the Enterprise Knowledge Assistant.
-- Run this in Supabase SQL Editor or through the Supabase CLI.

create extension if not exists pgcrypto;
create extension if not exists citext;

do $$
begin
    create type public.app_role as enum (
        'employee',
        'hr_admin',
        'devops_admin',
        'security_admin',
        'finance_admin',
        'admin'
    );
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type public.document_category as enum (
        'hr',
        'devops',
        'security',
        'finance',
        'technical',
        'general'
    );
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type public.document_status as enum (
        'uploaded',
        'processing',
        'ready',
        'failed',
        'archived'
    );
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type public.chat_message_role as enum (
        'user',
        'assistant',
        'system'
    );
exception
    when duplicate_object then null;
end $$;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email citext unique not null,
    full_name text,
    avatar_url text,
    role public.app_role not null default 'employee',
    department text,
    job_title text,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references public.profiles(id) on delete restrict,
    title text not null,
    description text,
    category public.document_category not null default 'general',
    storage_bucket text not null default 'company-documents',
    storage_path text not null unique,
    mime_type text not null,
    file_size_bytes bigint not null check (file_size_bytes > 0),
    checksum_sha256 text,
    status public.document_status not null default 'uploaded',
    error_message text,
    uploaded_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.document_pages (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.documents(id) on delete cascade,
    page_number integer not null check (page_number > 0),
    text_content text not null default '',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    unique (document_id, page_number)
);

create table if not exists public.document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.documents(id) on delete cascade,
    page_id uuid references public.document_pages(id) on delete set null,
    chunk_index integer not null check (chunk_index >= 0),
    content text not null,
    token_count integer check (token_count is null or token_count > 0),
    page_start integer check (page_start is null or page_start > 0),
    page_end integer check (page_end is null or page_end > 0),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    unique (document_id, chunk_index),
    check (page_end is null or page_start is null or page_end >= page_start)
);

create table if not exists public.conversations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.profiles(id) on delete cascade,
    title text not null default 'New conversation',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
    id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references public.conversations(id) on delete cascade,
    role public.chat_message_role not null,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists public.message_sources (
    id uuid primary key default gen_random_uuid(),
    message_id uuid not null references public.chat_messages(id) on delete cascade,
    document_id uuid not null references public.documents(id) on delete restrict,
    chunk_id uuid references public.document_chunks(id) on delete set null,
    page_number integer check (page_number is null or page_number > 0),
    relevance_score numeric(6, 5) check (
        relevance_score is null
        or (relevance_score >= 0 and relevance_score <= 1)
    ),
    quote text,
    created_at timestamptz not null default now()
);

create table if not exists public.audit_logs (
    id uuid primary key default gen_random_uuid(),
    actor_id uuid references public.profiles(id) on delete set null,
    action text not null,
    entity_type text not null,
    entity_id uuid,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_profiles_role on public.profiles(role);
create index if not exists idx_profiles_department on public.profiles(department);
create index if not exists idx_documents_owner_id on public.documents(owner_id);
create index if not exists idx_documents_category on public.documents(category);
create index if not exists idx_documents_status on public.documents(status);
create index if not exists idx_document_pages_document_id on public.document_pages(document_id);
create index if not exists idx_document_chunks_document_id on public.document_chunks(document_id);
create index if not exists idx_document_chunks_page_id on public.document_chunks(page_id);
create index if not exists idx_conversations_user_id on public.conversations(user_id);
create index if not exists idx_chat_messages_conversation_id on public.chat_messages(conversation_id);
create index if not exists idx_message_sources_message_id on public.message_sources(message_id);
create index if not exists idx_message_sources_document_id on public.message_sources(document_id);
create index if not exists idx_audit_logs_actor_id on public.audit_logs(actor_id);
create index if not exists idx_audit_logs_entity on public.audit_logs(entity_type, entity_id);

drop trigger if exists set_profiles_updated_at on public.profiles;
create trigger set_profiles_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

drop trigger if exists set_documents_updated_at on public.documents;
create trigger set_documents_updated_at
before update on public.documents
for each row execute function public.set_updated_at();

drop trigger if exists set_conversations_updated_at on public.conversations;
create trigger set_conversations_updated_at
before update on public.conversations
for each row execute function public.set_updated_at();

create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (
        id,
        email,
        full_name,
        avatar_url
    )
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name'),
        new.raw_user_meta_data ->> 'avatar_url'
    )
    on conflict (id) do update set
        email = excluded.email,
        full_name = coalesce(excluded.full_name, public.profiles.full_name),
        avatar_url = coalesce(excluded.avatar_url, public.profiles.avatar_url),
        updated_at = now();

    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_auth_user();

alter table public.profiles enable row level security;
alter table public.documents enable row level security;
alter table public.document_pages enable row level security;
alter table public.document_chunks enable row level security;
alter table public.conversations enable row level security;
alter table public.chat_messages enable row level security;
alter table public.message_sources enable row level security;
alter table public.audit_logs enable row level security;

create or replace function public.current_user_role()
returns public.app_role
language sql
stable
security definer
set search_path = public
as $$
    select role
    from public.profiles
    where id = auth.uid()
$$;

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
    select coalesce(public.current_user_role() = 'admin', false)
$$;

create or replace function public.can_manage_category(category public.document_category)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
    select coalesce(
        public.current_user_role() = 'admin'
        or (category = 'hr' and public.current_user_role() = 'hr_admin')
        or (category = 'devops' and public.current_user_role() = 'devops_admin')
        or (category = 'security' and public.current_user_role() = 'security_admin')
        or (category = 'finance' and public.current_user_role() = 'finance_admin'),
        false
    )
$$;

drop policy if exists "Users can read their own profile" on public.profiles;
create policy "Users can read their own profile"
on public.profiles
for select
to authenticated
using (id = auth.uid() or public.is_admin());

drop policy if exists "Admins can update profiles" on public.profiles;
create policy "Admins can update profiles"
on public.profiles
for update
to authenticated
using (public.is_admin())
with check (public.is_admin());

drop policy if exists "Authenticated users can read ready documents" on public.documents;
create policy "Authenticated users can read ready documents"
on public.documents
for select
to authenticated
using (status = 'ready' or owner_id = auth.uid() or public.can_manage_category(category));

drop policy if exists "Category managers can insert documents" on public.documents;
create policy "Authenticated users can insert their documents"
on public.documents
for insert
to authenticated
with check (owner_id = auth.uid());

drop policy if exists "Category managers can update documents" on public.documents;
create policy "Category managers can update documents"
on public.documents
for update
to authenticated
using (public.can_manage_category(category))
with check (public.can_manage_category(category));

drop policy if exists "Users can read pages for visible documents" on public.document_pages;
create policy "Users can read pages for visible documents"
on public.document_pages
for select
to authenticated
using (
    exists (
        select 1
        from public.documents d
        where d.id = public.document_pages.document_id
          and (d.status = 'ready' or d.owner_id = auth.uid() or public.can_manage_category(d.category))
    )
);

drop policy if exists "Users can read chunks for visible documents" on public.document_chunks;
create policy "Users can read chunks for visible documents"
on public.document_chunks
for select
to authenticated
using (
    exists (
        select 1
        from public.documents d
        where d.id = public.document_chunks.document_id
          and (d.status = 'ready' or d.owner_id = auth.uid() or public.can_manage_category(d.category))
    )
);

drop policy if exists "Users can manage their conversations" on public.conversations;
create policy "Users can manage their conversations"
on public.conversations
for all
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "Users can manage messages in their conversations" on public.chat_messages;
create policy "Users can manage messages in their conversations"
on public.chat_messages
for all
to authenticated
using (
    exists (
        select 1
        from public.conversations c
        where c.id = public.chat_messages.conversation_id
          and c.user_id = auth.uid()
    )
)
with check (
    exists (
        select 1
        from public.conversations c
        where c.id = public.chat_messages.conversation_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists "Users can read sources for their messages" on public.message_sources;
create policy "Users can read sources for their messages"
on public.message_sources
for select
to authenticated
using (
    exists (
        select 1
        from public.chat_messages m
        join public.conversations c on c.id = m.conversation_id
        where m.id = public.message_sources.message_id
          and c.user_id = auth.uid()
    )
);

drop policy if exists "Admins can read audit logs" on public.audit_logs;
create policy "Admins can read audit logs"
on public.audit_logs
for select
to authenticated
using (public.is_admin());

drop policy if exists "Authenticated users can insert audit logs" on public.audit_logs;
create policy "Authenticated users can insert audit logs"
on public.audit_logs
for insert
to authenticated
with check (actor_id = auth.uid() or actor_id is null);
