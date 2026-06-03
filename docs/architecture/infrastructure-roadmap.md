# Infrastructure Roadmap — What To Connect When

You do **not** need MongoDB, Docker, or Kubernetes for Phases 1–9.

## Already Connected (keep these running)

| Service | Purpose | Status |
|---------|---------|--------|
| **Supabase** | Auth, PostgreSQL, file storage | Required now |
| **Google OAuth** | Login | Required now |
| **FastAPI backend** | API, parsing, chunking | Local port 8000 |
| **Next.js frontend** | UI | Local port 3000 |

## Coming Soon (Phases 8–11)

| Service | Phase | Action needed |
|---------|-------|----------------|
| **SentenceTransformers** | 7 | `pip install -r requirements.txt` (done in Phase 7) |
| **ChromaDB** | 8 | `pip install` — local `./chroma_data` folder |
| **Groq or Gemini API** | 9+ | Add API key to `backend/.env` |

## Later (Phases 18–24)

| Service | Phase | Notes |
|---------|-------|-------|
| **Docker** | 18–19 | Package frontend + backend |
| **Docker Compose** | 19 | Run app + Chroma + Postgres together |
| **GitHub Actions** | 20 | CI/CD |
| **Vercel + Render** | 21 | Hosted frontend + backend |
| **Kubernetes (EKS)** | 22 | Production scale |
| **AWS S3 / RDS / EC2** | Future | Enterprise deployment |

## Not Used In This Project

| Technology | Why not |
|------------|---------|
| **MongoDB** | PostgreSQL (Supabase) is the source of truth |
| **Redis** | Optional later for caching — not in early phases |

## Your Checklist Right Now

```text
[x] Supabase project + migrations
[x] Google OAuth
[x] backend/.env + frontend/.env.local
[x] Phase 7: `pip install -r requirements.txt` + migration 0003
[x] Phase 8: ChromaDB (`pip install chromadb`)
[ ] Phase 9: add GROQ_API_KEY or GEMINI_API_KEY
```
