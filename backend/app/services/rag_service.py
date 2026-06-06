import logging
from collections.abc import AsyncGenerator
from typing import Any

from app.services.semantic_search_service import SearchHit, SemanticSearchService

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval augmented generation service."""

    def __init__(self, semantic_search_service: SemanticSearchService, llm: Any) -> None:
        self.semantic_search = semantic_search_service
        self.llm = llm

    def _build_prompt(self, query: str, chunks: list[dict[str, Any]]) -> str:
        context_parts = []
        for index, chunk in enumerate(chunks, start=1):
            source = chunk.get("metadata", {})
            text = str(chunk.get("document", "")).strip()
            source_id = source.get("document_id", "unknown")
            context_parts.append(f"[Context {index}] {text} (source: {source_id})")

        context = "\n".join(context_parts)
        return (
            "You are an enterprise knowledge assistant. Answer using only the "
            "provided context. If the answer cannot be derived from the context, "
            "respond with \"I don't have enough information.\"\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\n"
        )

    def _build_extractive_answer(self, hits: list[SearchHit]) -> str:
        if not hits:
            return (
                "I don't have enough information in your uploaded company "
                "documents to answer that."
            )

        strongest_hit = hits[0]
        source_name = strongest_hit.document_title or "the uploaded document"
        text = strongest_hit.content.strip()

        if len(text) > 900:
            text = f"{text[:900].rsplit(' ', 1)[0]}..."

        return (
            f"Based on {source_name}, the most relevant document text says:\n\n"
            f"{text}"
        )

    def _hits_to_prompt_chunks(self, hits: list[SearchHit]) -> list[dict[str, Any]]:
        return [
            {
                "metadata": {
                    "document_id": hit.document_id,
                    "document_title": hit.document_title,
                    "category": hit.category,
                    "page_number": hit.page_start,
                    "page_end": hit.page_end,
                },
                "document": hit.content,
                "distance": hit.relevance_score,
            }
            for hit in hits
        ]

    def _chunks_to_sources(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        sources = []
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            sources.append(
                {
                    "document_id": metadata.get("document_id", ""),
                    "page_number": metadata.get("page_number"),
                    "text": chunk.get("document", ""),
                }
            )
        return sources

    def _retrieve_hits(
        self,
        query: str,
        *,
        k: int,
        owner_id: str | None,
    ) -> list[SearchHit]:
        if owner_id is not None and hasattr(self.semantic_search, "search_for_owner"):
            return self.semantic_search.search_for_owner(query, owner_id, limit=k)

        query_vector = self.semantic_search.embedding_encoder.embed_texts([query])[0]
        return self.semantic_search.search(query_vector, limit=k)

    def answer_query(
        self,
        query: str,
        k: int = 5,
        owner_id: str | None = None,
    ) -> tuple[str, list[SearchHit] | list[dict[str, Any]]]:
        hits = self._retrieve_hits(query, k=k, owner_id=owner_id)
        if not hits:
            return self._build_extractive_answer(hits), []

        prompt_chunks = self._hits_to_prompt_chunks(hits)
        prompt = self._build_prompt(query, prompt_chunks)

        logger.info("RAG prompt built with %d chunks", len(prompt_chunks))
        try:
            llm_response = self.llm.invoke([{"role": "user", "content": prompt}])
            answer = getattr(llm_response, "content", str(llm_response)).strip()
        except Exception as exc:
            logger.exception("LLM invocation failed: %s", exc)
            answer = self._build_extractive_answer(hits)

        if owner_id is not None:
            return answer, hits

        return answer, self._chunks_to_sources(prompt_chunks)

    async def stream_answer(
        self,
        query: str,
        k: int = 5,
        owner_id: str | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        hits = self._retrieve_hits(query, k=k, owner_id=owner_id)
        prompt_chunks = self._hits_to_prompt_chunks(hits)
        sources = self._chunks_to_sources(prompt_chunks)

        yield {"type": "sources", "sources": sources}

        if not hits:
            yield {"type": "token", "token": self._build_extractive_answer(hits)}
            return

        prompt = self._build_prompt(query, prompt_chunks)
        logger.info("RAG streaming prompt built with %d chunks", len(prompt_chunks))

        try:
            async for chunk in self.llm.astream([{"role": "user", "content": prompt}]):
                token = getattr(chunk, "content", str(chunk))
                if token:
                    yield {"type": "token", "token": token}
        except Exception as exc:
            logger.warning("Falling back to non-async LLM streaming: %s", exc)
            if hasattr(self.llm, "stream"):
                try:
                    for chunk in self.llm.stream([{"role": "user", "content": prompt}]):
                        token = getattr(chunk, "content", str(chunk))
                        if token:
                            yield {"type": "token", "token": token}
                except Exception as stream_exc:
                    logger.exception("LLM stream fallback failed: %s", stream_exc)
                    yield {"type": "token", "token": self._build_extractive_answer(hits)}
            else:
                try:
                    llm_response = self.llm.invoke([{"role": "user", "content": prompt}])
                    yield {
                        "type": "token",
                        "token": getattr(llm_response, "content", str(llm_response)),
                    }
                except Exception as invoke_exc:
                    logger.exception("LLM invocation failed: %s", invoke_exc)
                    yield {"type": "token", "token": self._build_extractive_answer(hits)}
