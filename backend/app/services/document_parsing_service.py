import logging
from typing import Any

from fastapi import HTTPException, status

from app.parsers.pdf_parser import PdfParserService
from app.repositories.chunk_embedding_repository import ChunkEmbeddingRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_page_repository import DocumentPageRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.storage_repository import StorageRepository
from app.schemas.document import DocumentResponse, DocumentStatus
from app.services.document_chunking_service import DocumentChunkingService
from app.services.document_embedding_service import DocumentEmbeddingService
from app.services.document_vector_index_service import DocumentVectorIndexService

logger = logging.getLogger(__name__)


class DocumentParsingService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        document_page_repository: DocumentPageRepository,
        storage_repository: StorageRepository,
        chunking_service: DocumentChunkingService,
        embedding_service: DocumentEmbeddingService,
        vector_index_service: DocumentVectorIndexService,
        pdf_parser: PdfParserService | None = None,
        document_chunk_repository: DocumentChunkRepository | None = None,
        chunk_embedding_repository: ChunkEmbeddingRepository | None = None,
    ) -> None:
        self.document_repository = document_repository
        self.document_page_repository = document_page_repository
        self.storage_repository = storage_repository
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.vector_index_service = vector_index_service
        self.pdf_parser = pdf_parser or PdfParserService()
        self.document_chunk_repository = document_chunk_repository
        self.chunk_embedding_repository = chunk_embedding_repository

    def parse_and_persist(self, document: dict[str, Any], content: bytes) -> DocumentResponse:
        document_id = str(document["id"])

        self.document_repository.update_status(document_id, DocumentStatus.processing)

        try:
            parsed_pages = self.pdf_parser.parse(content)

            if not parsed_pages:
                return self._to_response(
                    document,
                    self.document_repository.update_status(
                        document_id,
                        DocumentStatus.failed,
                        error_message="PDF contains no pages",
                    ),
                )

            self.document_page_repository.delete_for_document(document_id)
            page_rows = [
                {
                    "page_number": page.page_number,
                    "text_content": page.text_content,
                    "metadata": page.metadata,
                }
                for page in parsed_pages
            ]
            inserted_pages = self.document_page_repository.insert_many(document_id, page_rows)

            pages_with_text = sum(1 for page in parsed_pages if page.text_content)
            if pages_with_text == 0:
                updated = self.document_repository.update_status(
                    document_id,
                    DocumentStatus.failed,
                    error_message=(
                        "No extractable text found in PDF "
                        "(it may be scanned images only)"
                    ),
                )
            else:
                chunk_count = self.chunking_service.chunk_and_persist(document_id, inserted_pages)
                if chunk_count == 0:
                    updated = self.document_repository.update_status(
                        document_id,
                        DocumentStatus.failed,
                        error_message="Pages were parsed but chunking produced no content",
                    )
                else:
                    updated = self._embed_index_and_finalize(document_id, document)

            logger.info(
                "Document parsed",
                extra={
                    "document_id": document_id,
                    "page_count": len(parsed_pages),
                    "pages_with_text": pages_with_text,
                    "status": updated["status"],
                },
            )
            return self._to_response(document, updated)

        except Exception as exc:
            logger.exception("PDF parsing failed for document %s", document_id)
            updated = self.document_repository.update_status(
                document_id,
                DocumentStatus.failed,
                error_message=str(exc)[:500],
            )
            return self._to_response(document, updated)

    def _embed_index_and_finalize(
        self,
        document_id: str,
        document: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            embedding_count = self.embedding_service.embed_document(document_id)
            if embedding_count == 0:
                return self.document_repository.update_status(
                    document_id,
                    DocumentStatus.failed,
                    error_message="Chunks were created but embedding generation failed",
                )

            vector_count = self.vector_index_service.index_document(document_id)
            if vector_count == 0:
                return self.document_repository.update_status(
                    document_id,
                    DocumentStatus.failed,
                    error_message="Embeddings were created but Chroma indexing failed",
                )

            return self.document_repository.update_status(document_id, DocumentStatus.ready)
        except Exception as exc:
            logger.exception("Processing failed for document %s", document_id)
            return self.document_repository.update_status(
                document_id,
                DocumentStatus.failed,
                error_message=f"Processing failed: {str(exc)[:400]}",
            )

    @staticmethod
    def _to_response(document: dict[str, Any], updated: dict[str, Any]) -> DocumentResponse:
        return DocumentResponse.model_validate({**document, **updated})

    def parse_for_owner(self, document_id: str, owner_id: str) -> DocumentResponse:
        document = self.document_repository.get_for_owner(document_id, owner_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        if document["status"] == DocumentStatus.processing.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document is already being parsed",
            )

        content = self.storage_repository.download_pdf(
            bucket=document["storage_bucket"],
            path=document["storage_path"],
        )
        return self.parse_and_persist(document, content)

    def reprocess_by_id(self, document_id: str) -> DocumentResponse:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        content = self.storage_repository.download_pdf(
            bucket=document["storage_bucket"],
            path=document["storage_path"],
        )
        return self.parse_and_persist(document, content)

    def get_document_with_pages(
        self,
        document_id: str,
        owner_id: str,
    ) -> tuple[DocumentResponse, list[dict[str, Any]], int, int, int, str | None]:
        document = self.document_repository.get_for_owner(document_id, owner_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        pages = self.document_page_repository.list_for_document(document_id)
        chunk_count = 0
        embedding_count = 0
        embedding_model: str | None = None
        vector_count = 0
        if self.document_chunk_repository is not None:
            chunk_count = self.document_chunk_repository.count_for_document(document_id)
        if self.chunk_embedding_repository is not None:
            embedding_count = self.chunk_embedding_repository.count_for_document(document_id)
            embedding_model = self.chunk_embedding_repository.get_model_name_for_document(
                document_id
            )
        vector_count = self.vector_index_service.count_indexed_vectors(document_id)

        return (
            DocumentResponse.model_validate(document),
            pages,
            chunk_count,
            embedding_count,
            vector_count,
            embedding_model,
        )

    def embed_for_owner(self, document_id: str, owner_id: str) -> int:
        document = self.document_repository.get_for_owner(document_id, owner_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        chunk_count = self.document_chunk_repository.count_for_document(document_id)
        if chunk_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no chunks. Run parsing first.",
            )

        count = self.embedding_service.embed_document(document_id)
        self.vector_index_service.index_document(document_id)
        return count

    def index_for_owner(self, document_id: str, owner_id: str) -> int:
        document = self.document_repository.get_for_owner(document_id, owner_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        embedding_count = self.chunk_embedding_repository.count_for_document(document_id)
        if embedding_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no embeddings. Run parsing or embed first.",
            )

        return self.vector_index_service.index_document(document_id)

    def get_chunks_for_document(
        self,
        document_id: str,
        owner_id: str,
        *,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        document = self.document_repository.get_for_owner(document_id, owner_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        if self.document_chunk_repository is None:
            return []

        return self.document_chunk_repository.list_for_document(document_id, limit=limit)
