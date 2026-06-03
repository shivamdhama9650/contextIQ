# Enterprise Knowledge Assistant

A production-grade learning project for building an internal company knowledge assistant with document upload, retrieval augmented generation, authentication, role-based access control, agents, analytics, and deployment automation.

## Current Capabilities

- Next.js frontend with authenticated dashboard, document upload, search, chat, admin, and analytics pages
- FastAPI backend with JWT authentication, Supabase integration, RBAC, document processing, RAG, and LangGraph agent workflow
- Supabase PostgreSQL schema for profiles, documents, pages, chunks, embeddings, and conversations
- Supabase Storage for uploaded PDFs
- PDF parsing with PyMuPDF
- Chunking, SentenceTransformers embeddings, and ChromaDB vector search
- Groq/Gemini-ready LLM layer with grounded fallback behavior
- Source-aware chat assistant that answers from indexed company documents
- Admin tools for role management, document inspection, analytics, and document reprocessing

## Repository Layout

```text
enterprise-knowledge-assistant/
  backend/
    app/
      agents/
      api/
      chunking/
      core/
      db/
      embeddings/
      parsers/
      repositories/
      schemas/
      services/
      vector/
    tests/
    pyproject.toml
    requirements.txt
  docs/
    architecture/
    dependencies.md
  frontend/
    app/
    lib/
    package.json
    tsconfig.json
  supabase/
    migrations/
  .env.example
```

## Local Prerequisites

- Node.js 20 or newer
- npm 10 or newer
- Python 3.11 or newer
- Git
- Supabase project
- Groq API key or Gemini API key

On Windows PowerShell, use `npm.cmd` if `npm` is blocked by execution policy.

## Environment Setup

Copy the example environment file and fill in your real values:

```powershell
Copy-Item .env.example .env
```

Frontend values:

```text
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Backend values:

```text
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=
```

The frontend only uses public Supabase values. The backend keeps privileged values server-side.

## Quick Start

Backend:

```powershell
cd enterprise-knowledge-assistant/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
cd enterprise-knowledge-assistant/frontend
npm.cmd install
npm.cmd run dev
```

Expected URLs:

```text
Frontend: http://localhost:3000
Backend health: http://localhost:8000/health
Backend docs: http://localhost:8000/docs
```

## Useful Checks

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Frontend:

```powershell
cd frontend
npm.cmd run type-check
npm.cmd run build
```

## Notes

Architecture learning notes are stored in `docs/architecture/`. Those files preserve the step-by-step build history, while the app UI is kept product-facing for employees and admins.
