import logging
from typing import Any

from app.embeddings.sentence_embedding_service import EmbeddingEncoder
from app.repositories.chunk_embedding_repository import ChunkEmbeddingRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository

logger = logging.getLogger(__name__)


class DocumentEmbeddingService:
    def __init__(
        self,
        document_chunk_repository: DocumentChunkRepository,
        chunk_embedding_repository: ChunkEmbeddingRepository,
        embedding_encoder: EmbeddingEncoder,
        *,
        batch_size: int = 32,
    ) -> None:
        self.document_chunk_repository = document_chunk_repository
        self.chunk_embedding_repository = chunk_embedding_repository
        self.embedding_encoder = embedding_encoder
        self.batch_size = batch_size

    def embed_document(self, document_id: str) -> int:
        chunks = self.document_chunk_repository.list_for_document(document_id, limit=10_000)
        if not chunks:
            logger.warning("No chunks to embed for document %s", document_id)
            return 0

        self.chunk_embedding_repository.delete_for_document(document_id)

        texts = [str(chunk["content"]) for chunk in chunks]
        dimensions = getattr(self.embedding_encoder, "dimensions", None)
        all_vectors: list[list[float]] = []

        for start in range(0, len(texts), self.batch_size):
            batch_texts = texts[start : start + self.batch_size]
            all_vectors.extend(self.embedding_encoder.embed_texts(batch_texts))

        if dimensions is None and all_vectors:
            dimensions = len(all_vectors[0])
        elif dimensions is None:
            dimensions = 0

        model_name = self.embedding_encoder.model_name
        rows: list[dict[str, Any]] = []
        for chunk, vector in zip(chunks, all_vectors, strict=True):
            rows.append(
                {
                    "chunk_id": chunk["id"],
                    "document_id": document_id,
                    "model_name": model_name,
                    "dimensions": len(vector),
                    "embedding": vector,
                }
            )

        self.chunk_embedding_repository.insert_many(rows)
        logger.info(
            "Embeddings stored",
            extra={
                "document_id": document_id,
                "embedding_count": len(rows),
                "model_name": model_name,
                "dimensions": dimensions,
            },
        )
        return len(rows)
