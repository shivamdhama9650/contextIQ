#!/usr/bin/env python3
"""
Simple diagnostics script for the Enterprise Knowledge Assistant.
It checks that required environment variables are present and that the
connected services (Supabase, Gemini, Groq, ChromaDB, embedding model) are reachable.
All output uses plain ASCII for Windows console compatibility.
"""
import os
from pathlib import Path


# Helper to print status messages
def status(step: str, ok: bool, detail: str = ""):
    icon = "[OK]" if ok else "[FAIL]"
    print(f"{step} {icon} {detail}")

# ---------------------------------------------------------------------
# 1. Load environment variables from .env (if present)
# ---------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
    status("[1] .env loaded", True)
except Exception as e:
    status("[1] .env loaded", False, str(e))
    # continue – env vars may already be in the process environment

# ---------------------------------------------------------------------
# 2. Supabase connectivity (uses anon key – enough for a simple ping)
# ---------------------------------------------------------------------
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL or SUPABASE_ANON_KEY missing")
    from supabase import create_client
    client = create_client(supabase_url, supabase_key)
    # Simple request – list tables (or a harmless query)
    client.table("profiles").select("id", count="exact").limit(1).execute()
    status("[2] Supabase connectivity", True)
except Exception as e:
    status("[2] Supabase connectivity", False, str(e))

# ---------------------------------------------------------------------
# 3. Gemini API key (Google Generative AI)
# ---------------------------------------------------------------------
try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not set")
    from langchain_core.messages import HumanMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=gemini_key,
        temperature=0,
    )
    resp = llm.invoke([HumanMessage(content="Reply with the word OK")])
    status("[3] Gemini API key", True, f"model replied: '{resp.content.strip()}'")
except Exception as e:
    status("[3] Gemini API key", False, str(e))

# ---------------------------------------------------------------------
# 4. Groq API key
# ---------------------------------------------------------------------
try:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not set")
    from langchain_core.messages import HumanMessage
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_key, temperature=0)
    resp = llm.invoke([HumanMessage(content="Reply with the word OK")])
    status("[4] Groq API key", True, f"model replied: '{resp.content.strip()}'")
except Exception as e:
    status("[4] Groq API key", False, str(e))

# ---------------------------------------------------------------------
# 5. ChromaDB (vector store) – uses settings from .env
# ---------------------------------------------------------------------
try:
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    chroma_collection = os.getenv("CHROMA_COLLECTION_NAME", "documents")
    from app.vector.chroma_store import ChromaVectorStore
    store = ChromaVectorStore(
        persist_directory=str(Path(chroma_dir).resolve()),
        collection_name=chroma_collection,
    )
    cnt = store.collection.count()
    status("[5] ChromaDB", True, f"collection '{chroma_collection}' has {cnt} vectors")
except Exception as e:
    status("[5] ChromaDB", False, str(e))

# ---------------------------------------------------------------------
# 6. Embedding model (sentence transformer)
# ---------------------------------------------------------------------
try:
    embed_model = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    from app.embeddings.sentence_embedding_service import SentenceEmbeddingService
    encoder = SentenceEmbeddingService(embed_model)
    vec = encoder.embed_texts(["hello world"])
    status("[6] Embedding model", True, f"dim={len(vec[0])}")
except Exception as e:
    status("[6] Embedding model", False, str(e))

print("\n" + "=" * 55)
print("Diagnostics complete. Review any [FAIL] lines above.")
print("=" * 55)
