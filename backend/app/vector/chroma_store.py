import logging
from typing import Any

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Persistent ChromaDB collection for semantic chunk retrieval."""

    def __init__(self, persist_directory: str, collection_name: str) -> None:
        import chromadb

        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def delete_by_document(self, document_id: str) -> None:
        existing = self.collection.get(where={"document_id": document_id}, include=[])
        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])

    def upsert(
        self,
        *,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        if not ids:
            return

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        *,
        n_results: int,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

    def count_for_document(self, document_id: str) -> int:
        result = self.collection.get(where={"document_id": document_id}, include=[])
        return len(result["ids"])
