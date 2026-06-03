from uuid import uuid4

from app.services.document_embedding_service import DocumentEmbeddingService


class FakeChunkRepository:
    def __init__(self, chunks: list[dict]) -> None:
        self.chunks = chunks

    def list_for_document(self, document_id: str, *, limit: int = 100) -> list[dict]:
        return self.chunks


class FakeEmbeddingRepository:
    def __init__(self) -> None:
        self.deleted_for: list[str] = []
        self.inserted: list[dict] = []

    def delete_for_document(self, document_id: str) -> None:
        self.deleted_for.append(document_id)
        self.inserted = [row for row in self.inserted if row["document_id"] != document_id]

    def insert_many(self, rows: list[dict]) -> list[dict]:
        self.inserted.extend(rows)
        return rows


class FakeEncoder:
    model_name = "test-embedding-model"
    dimensions = 4

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]


def test_embed_document_persists_vectors() -> None:
    document_id = str(uuid4())
    chunk_id = str(uuid4())
    chunk_repository = FakeChunkRepository(
        [
            {
                "id": chunk_id,
                "document_id": document_id,
                "content": "Leave policy for full-time employees",
            }
        ]
    )
    embedding_repository = FakeEmbeddingRepository()

    service = DocumentEmbeddingService(
        document_chunk_repository=chunk_repository,
        chunk_embedding_repository=embedding_repository,
        embedding_encoder=FakeEncoder(),
    )

    count = service.embed_document(document_id)

    assert count == 1
    assert document_id in embedding_repository.deleted_for
    assert len(embedding_repository.inserted) == 1
    assert embedding_repository.inserted[0]["chunk_id"] == chunk_id
    assert embedding_repository.inserted[0]["dimensions"] == 4
    assert len(embedding_repository.inserted[0]["embedding"]) == 4
