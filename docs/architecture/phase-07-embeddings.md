# Phase 7: Embedding Generation

## What We Are Building

Each text chunk is converted into a **dense vector** using **SentenceTransformers** (`all-MiniLM-L6-v2` by default) and stored in `chunk_embeddings`.

## Why It Is Needed

RAG retrieves content by **semantic similarity**, not keyword match. Embeddings map text meaning into numbers so similar questions find similar policy passages.

## Pipeline

```text
document_chunks → SentenceTransformer.encode() → chunk_embeddings (JSON vectors)
                                              → Phase 8: ChromaDB index
```

## Configuration

| Variable | Default |
|----------|---------|
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` |
| `EMBEDDING_BATCH_SIZE` | `32` |

## SQL Migration

Run in Supabase SQL Editor:

`supabase/migrations/0003_chunk_embeddings.sql`

## Commands

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

First upload after install downloads the model (~80MB). This can take 1–2 minutes once.

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/documents/upload` | Upload + parse + chunk + embed |
| POST | `/documents/{id}/embed` | Re-generate embeddings only |

## How To Test

1. Apply migration `0003`.
2. Upload a PDF.
3. Document detail shows **embedding count** matching **chunk count**.
4. Supabase `chunk_embeddings` table has rows with `embedding` JSON arrays.

## Common Errors

| Error | Fix |
|-------|-----|
| Table `chunk_embeddings` not found | Run migration 0003 |
| `Embedding failed: No module named 'sentence_transformers'` | `pip install -r requirements.txt` |
| Slow first upload | Normal — model download + CPU encoding |
