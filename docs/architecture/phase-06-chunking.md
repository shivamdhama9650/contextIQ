# Phase 6: Chunking Strategy

## What We Are Building

After PDF pages are stored, each page's text is split into **overlapping chunks** (~1000 characters, 200 overlap) and saved in `document_chunks`.

## Why It Is Needed

LLMs and embedding models have context limits. Chunking keeps retrieval precise: answers cite small relevant passages instead of entire documents.

## Chunking Flow

```text
document_pages → TextChunker → document_chunks → (Phase 7 embeddings) → ChromaDB
```

## Configuration

| Setting | Default |
|---------|---------|
| Chunk size | 1000 characters |
| Overlap | 200 characters |

## How To Test

1. Upload a multi-page PDF.
2. Open document detail → confirm **chunk count** > 0.
3. Supabase Table Editor → `document_chunks` rows for your `document_id`.

## Re-chunk Existing Documents

Click **Retry parsing** on a document — pages and chunks are rebuilt.
