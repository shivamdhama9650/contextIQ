import logging
from typing import Any

from app.chunking.text_chunker import TextChunker
from app.repositories.document_chunk_repository import DocumentChunkRepository

logger = logging.getLogger(__name__)


class DocumentChunkingService:
    def __init__(
        self,
        document_chunk_repository: DocumentChunkRepository,
        text_chunker: TextChunker | None = None,
    ) -> None:
        self.document_chunk_repository = document_chunk_repository
        self.text_chunker = text_chunker or TextChunker()

    def chunk_and_persist(self, document_id: str, pages: list[dict[str, Any]]) -> int:
        self.document_chunk_repository.delete_for_document(document_id)

        drafts = self.text_chunker.chunk_pages(pages)
        if not drafts:
            logger.warning("No chunks created for document %s", document_id)
            return 0

        rows = [
            {
                "page_id": draft.page_id,
                "chunk_index": draft.chunk_index,
                "content": draft.content,
                "token_count": draft.token_count,
                "page_start": draft.page_start,
                "page_end": draft.page_end,
                "metadata": draft.metadata,
            }
            for draft in drafts
        ]
        self.document_chunk_repository.insert_many(document_id, rows)

        logger.info(
            "Document chunked",
            extra={"document_id": document_id, "chunk_count": len(rows)},
        )
        return len(rows)
