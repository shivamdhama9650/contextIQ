import logging
from dataclasses import dataclass

from app.embeddings.sentence_embedding_service import EmbeddingEncoder
from app.vector.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    document_id: str
    document_title: str
    category: str
    content: str
    page_start: int
    page_end: int
    relevance_score: float


class SemanticSearchService:
    def __init__(
        self,
        chroma_store: ChromaVectorStore,
        embedding_encoder: EmbeddingEncoder,
    ) -> None:
        self.chroma_store = chroma_store
        self.embedding_encoder = embedding_encoder

    def search_for_owner(
        self,
        query: str,
        owner_id: str,
        *,
        limit: int = 5,
    ) -> list[SearchHit]:
        query = query.strip()
        if not query:
            return []

        query_vector = self.embedding_encoder.embed_texts([query])[0]
        results = self.chroma_store.search(
            query_vector,
            n_results=limit,
            where={"owner_id": owner_id},
        )

        return self._parse_results(results)

    def search(self, query_vector: list[float], limit: int = 5) -> list[SearchHit]:
        """Search for similar chunks given a pre‑computed query embedding.

        This wraps the Chroma store and returns a list of ``SearchHit`` objects.
        """
        results = self.chroma_store.search(query_vector, n_results=limit)
        return self._parse_results(results)

    def _parse_results(self, results: dict) -> list[SearchHit]:
        ids = results.get("ids") or [[]]
        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]

        if not ids or not ids[0]:
            return []

        hits: list[SearchHit] = []
        for index, chunk_id in enumerate(ids[0]):
            metadata = metadatas[0][index] if metadatas[0] else {}
            distance = distances[0][index] if distances[0] else 1.0
            # Chroma cosine distance: lower is more similar. Convert to 0-1 score.
            relevance = max(0.0, min(1.0, 1.0 - float(distance)))

            hits.append(
                SearchHit(
                    chunk_id=str(chunk_id),
                    document_id=str(metadata.get("document_id", "")),
                    document_title=str(metadata.get("document_title", "")),
                    category=str(metadata.get("category", "")),
                    content=str(documents[0][index] if documents[0] else ""),
                    page_start=int(metadata.get("page_start") or 0),
                    page_end=int(metadata.get("page_end") or 0),
                    relevance_score=round(relevance, 4),
                )
            )

        return hits
