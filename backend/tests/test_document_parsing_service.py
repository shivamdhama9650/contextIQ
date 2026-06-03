from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.parsers.pdf_parser import PdfParserService
from app.schemas.document import DocumentStatus
from app.services.document_chunking_service import DocumentChunkingService
from app.services.document_embedding_service import DocumentEmbeddingService
from app.services.document_parsing_service import DocumentParsingService
from tests.test_pdf_parser import make_sample_pdf


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.status_updates: list[tuple[str, DocumentStatus]] = []
        self.documents: dict[str, dict] = {}

    def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        *,
        error_message: str | None = None,
    ) -> dict:
        self.status_updates.append((document_id, status))
        record = dict(self.documents[document_id])
        record["status"] = status.value
        record["error_message"] = error_message
        record["updated_at"] = datetime.now(UTC).isoformat()
        self.documents[document_id] = record
        return record

    def get_for_owner(self, document_id: str, owner_id: str) -> dict | None:
        record = self.documents.get(document_id)
        if record is None or record["owner_id"] != owner_id:
            return None
        return record


class FakeStorageRepository:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def download_pdf(self, bucket: str, path: str) -> bytes:
        return self.content


class FakeDocumentChunkRepository:
    def __init__(self) -> None:
        self.inserted: list[dict] = []

    def delete_for_document(self, document_id: str) -> None:
        self.inserted = [row for row in self.inserted if row["document_id"] != document_id]

    def insert_many(self, document_id: str, chunks: list[dict]) -> list[dict]:
        rows = []
        for chunk in chunks:
            row = {"id": str(uuid4()), "document_id": document_id, **chunk}
            rows.append(row)
            self.inserted.append(row)
        return rows

    def list_for_document(self, document_id: str, *, limit: int = 100) -> list[dict]:
        return [row for row in self.inserted if row["document_id"] == document_id][:limit]

    def count_for_document(self, document_id: str) -> int:
        return len([row for row in self.inserted if row["document_id"] == document_id])


class FakeChunkEmbeddingRepository:
    def __init__(self) -> None:
        self.inserted: list[dict] = []

    def delete_for_document(self, document_id: str) -> None:
        self.inserted = [row for row in self.inserted if row["document_id"] != document_id]

    def insert_many(self, rows: list[dict]) -> list[dict]:
        self.inserted.extend(rows)
        return rows

    def count_for_document(self, document_id: str) -> int:
        return len([row for row in self.inserted if row["document_id"] == document_id])

    def get_model_name_for_document(self, document_id: str) -> str | None:
        for row in self.inserted:
            if row["document_id"] == document_id:
                return row["model_name"]
        return None


class FakeEncoder:
    model_name = "test-model"
    dimensions = 4

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]


class FakeVectorIndexService:
    def index_document(self, document_id: str) -> int:
        return 1

    def count_indexed_vectors(self, document_id: str) -> int:
        return 1


class FakeDocumentPageRepository:
    def __init__(self) -> None:
        self.pages: list[dict] = []

    def delete_for_document(self, document_id: str) -> None:
        self.pages = []

    def insert_many(self, document_id: str, pages: list[dict]) -> list[dict]:
        rows = []
        for page in pages:
            row = {"id": str(uuid4()), "document_id": document_id, **page}
            rows.append(row)
            self.pages.extend(rows)
        return rows


@pytest.mark.anyio
async def test_parse_and_persist_marks_document_ready() -> None:
    document_id = str(uuid4())
    owner_id = str(uuid4())
    document_repository = FakeDocumentRepository()
    now = datetime.now(UTC).isoformat()
    document_repository.documents[document_id] = {
        "id": document_id,
        "owner_id": owner_id,
        "title": "Security Policy",
        "category": "security",
        "storage_bucket": "company-documents",
        "storage_path": f"{owner_id}/{document_id}/policy.pdf",
        "mime_type": "application/pdf",
        "file_size_bytes": 1024,
        "checksum_sha256": "abc",
        "status": DocumentStatus.uploaded.value,
        "error_message": None,
        "uploaded_at": now,
        "updated_at": now,
    }
    chunk_repository = FakeDocumentChunkRepository()
    embedding_repository = FakeChunkEmbeddingRepository()
    page_repository = FakeDocumentPageRepository()
    pdf_bytes = make_sample_pdf("Password must be 12 characters.")

    service = DocumentParsingService(
        document_repository=document_repository,
        document_page_repository=page_repository,
        storage_repository=FakeStorageRepository(pdf_bytes),
        chunking_service=DocumentChunkingService(chunk_repository),
        embedding_service=DocumentEmbeddingService(
            document_chunk_repository=chunk_repository,
            chunk_embedding_repository=embedding_repository,
            embedding_encoder=FakeEncoder(),
        ),
        vector_index_service=FakeVectorIndexService(),
        document_chunk_repository=chunk_repository,
        chunk_embedding_repository=embedding_repository,
        pdf_parser=PdfParserService(),
    )

    result = service.parse_and_persist(document_repository.documents[document_id], pdf_bytes)

    assert result.status == DocumentStatus.ready
    assert len(page_repository.pages) == 1
    assert len(chunk_repository.inserted) >= 1
    assert len(embedding_repository.inserted) >= 1
    assert "Password must be" in chunk_repository.inserted[0]["content"]
    assert document_repository.status_updates[0][1] == DocumentStatus.processing
    assert document_repository.status_updates[-1][1] == DocumentStatus.ready
