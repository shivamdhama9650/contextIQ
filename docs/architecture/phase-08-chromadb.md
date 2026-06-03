# Phase 8: ChromaDB Vector Database

## What We Are Building

Embeddings from PostgreSQL are copied into a **local ChromaDB** collection for fast semantic similarity search.

## Why It Is Needed

PostgreSQL stores business data and vectors as JSON, but vector search at scale belongs in a vector database. Chroma provides cosine similarity search filtered by `owner_id`.

## Architecture

```text
chunk_embeddings (Supabase)  →  index  →  ChromaDB (./chroma_data)
User query                 →  embed  →  Chroma search  →  ranked chunks
```

## Configuration

| Variable | Default |
|----------|---------|
| `CHROMA_PERSIST_DIR` | `./chroma_data` |
| `CHROMA_COLLECTION_NAME` | `company_knowledge` |

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/search` | Semantic search across your documents |
| POST | `/documents/{id}/index` | Re-index one document in Chroma |

Upload and parse automatically index vectors.

## Commands

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## How To Test

1. Upload a PDF (or re-parse an existing one).
2. Open **http://localhost:3000/search**.
3. Ask a question related to your PDF text.
4. Confirm ranked chunks with relevance scores.

## Common Errors

| Error | Fix |
|-------|-----|
| No search results | Re-upload or POST `/documents/{id}/index` |
| `No module named 'chromadb'` | `pip install -r requirements.txt` |
| Stale results after re-parse | Re-parse re-indexes automatically |
