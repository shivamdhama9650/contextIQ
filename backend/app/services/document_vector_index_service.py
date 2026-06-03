import logging
from typing import Any

from app.repositories.chunk_embedding_repository import ChunkEmbeddingRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.vector.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class DocumentVectorIndexService:
    def __init__(
        self,
        chroma_store: ChromaVectorStore,
        chunk_embedding_repository: ChunkEmbeddingRepository,
        document_chunk_repository: DocumentChunkRepository,
        document_repository: DocumentRepository,
    ) -> None:
        self.chroma_store = chroma_store
        self.chunk_embedding_repository = chunk_embedding_repository
        self.document_chunk_repository = document_chunk_repository
        self.document_repository = document_repository

    def index_document(self, document_id: str) -> int:
        document = self._get_document_record(document_id)
        embeddings = self.chunk_embedding_repository.list_for_document(document_id)
        if not embeddings:
            logger.warning("No embeddings to index for document %s", document_id)
            return 0

        chunks = {
            str(chunk["id"]): chunk
            for chunk in self.document_chunk_repository.list_for_document(
                document_id,
                limit=10_000,
            )
        }

        ids: list[str] = []
        vectors: list[list[float]] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for row in embeddings:
            chunk_id = str(row["chunk_id"])
            chunk = chunks.get(chunk_id)
            if chunk is None:
                continue

            ids.append(chunk_id)
            vectors.append(list(row["embedding"]))
            documents.append(str(chunk["content"]))
            metadatas.append(
                {
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "owner_id": str(document["owner_id"]),
                    "category": str(document["category"]),
                    "document_title": str(document["title"]),
                    "chunk_index": int(chunk["chunk_index"]),
                    "page_start": int(chunk["page_start"] or 0),
                    "page_end": int(chunk["page_end"] or 0),
                }
            )

        self.chroma_store.delete_by_document(document_id)
        self.chroma_store.upsert(
            ids=ids,
            embeddings=vectors,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(
            "Chroma index updated",
            extra={"document_id": document_id, "vector_count": len(ids)},
        )
        return len(ids)

    def count_indexed_vectors(self, document_id: str) -> int:
        return self.chroma_store.count_for_document(document_id)

    def _get_document_record(self, document_id: str) -> dict[str, Any]:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise ValueError(f"Document {document_id} not found")
        return document
