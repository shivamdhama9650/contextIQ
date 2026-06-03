# Project Dependencies

This file records every runtime and package dependency used by the project so a developer copying the repository can understand what to install and why it exists.

## System Dependencies

| Dependency | Version | Why It Is Needed |
| --- | --- | --- |
| Node.js | 20+ | Runs the Next.js frontend and frontend build tooling. |
| npm | 10+ | Installs frontend packages and runs frontend scripts. |
| Python | 3.11+ | Runs the FastAPI backend and AI processing libraries added in later phases. |
| Git | 2.40+ | Version control and CI/CD integration. |

## Frontend Packages

| Package | Why It Is Needed |
| --- | --- |
| `next` | Production React framework for routing, rendering, and Vercel deployment. |
| `react` | UI component library used by Next.js. |
| `react-dom` | Browser DOM renderer for React. |
| `@supabase/supabase-js` | Supabase JavaScript client for auth and data access. |
| `@supabase/ssr` | Supabase helper package for cookie-based auth in Next.js server rendering. |
| `lucide-react` | Icon library for clean application UI controls. |
| `typescript` | Static typing for safer frontend code. |
| `tailwindcss` | Utility-first CSS framework. |
| `postcss` | CSS processing used by Tailwind. |
| `autoprefixer` | Adds vendor prefixes to generated CSS. |
| `eslint` | Static analysis for frontend code quality. |
| `eslint-config-next` | Next.js-specific ESLint rules. |
| `@types/node` | TypeScript types for Node.js APIs. |
| `@types/react` | TypeScript types for React. |
| `@types/react-dom` | TypeScript types for React DOM. |

Install frontend packages:

```powershell
cd frontend
npm.cmd install
```

The exact installed frontend dependency tree is captured in:

```text
frontend/package-lock.json
```

## Backend Packages

| Package | Why It Is Needed |
| --- | --- |
| `fastapi` | Python API framework. |
| `uvicorn[standard]` | ASGI server used to run FastAPI. |
| `pydantic-settings` | Environment-based application configuration. |
| `email-validator` | Validates email-shaped fields in Pydantic schemas. |
| `httpx` | HTTP client used by tests and future service integrations. |
| `PyJWT[crypto]` | JWT verification using cryptographic signing keys. |
| `python-multipart` | Parses `multipart/form-data` requests for file uploads in FastAPI. |
| `pytest` | Backend test runner. |
| `ruff` | Python linting and formatting checks. |
| `supabase` | Python client for server-side Supabase database and storage operations. |
| `langgraph` | Graph-based orchestration for the multi-agent workflow. |

Install backend packages:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The exact installed backend dependency tree is captured in:

```text
backend/requirements-lock.txt
```

Use `requirements.txt` for normal development installs. Use `requirements-lock.txt` when you need to reproduce the exact package versions from this phase.
