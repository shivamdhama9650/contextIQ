from uuid import uuid4

from app.services.document_vector_index_service import DocumentVectorIndexService


class FakeChromaStore:
    def __init__(self) -> None:
        self.records: dict[str, list[dict]] = {}

    def delete_by_document(self, document_id: str) -> None:
        self.records[document_id] = []

    def upsert(self, *, ids, embeddings, documents, metadatas) -> None:
        document_id = metadatas[0]["document_id"] if metadatas else "unknown"
        self.records[document_id] = [
            {"id": chunk_id, "content": doc, "metadata": meta}
            for chunk_id, doc, meta in zip(ids, documents, metadatas, strict=True)
        ]

    def count_for_document(self, document_id: str) -> int:
        return len(self.records.get(document_id, []))


class FakeDocumentRepository:
    def get_by_id(self, document_id: str) -> dict | None:
        return {
            "id": document_id,
            "owner_id": str(uuid4()),
            "title": "Leave Policy",
            "category": "hr",
        }


class FakeChunkEmbeddingRepository:
    def list_for_document(self, document_id: str) -> list[dict]:
        return [
            {
                "chunk_id": "chunk-1",
                "document_id": document_id,
                "embedding": [0.1, 0.2, 0.3],
            }
        ]


class FakeDocumentChunkRepository:
    def list_for_document(self, document_id: str, *, limit: int = 100) -> list[dict]:
        return [
            {
                "id": "chunk-1",
                "document_id": document_id,
                "content": "Apply for leave via HR portal",
                "chunk_index": 0,
                "page_start": 1,
                "page_end": 1,
            }
        ]


def test_index_document_upserts_into_chroma() -> None:
    document_id = str(uuid4())
    chroma = FakeChromaStore()

    service = DocumentVectorIndexService(
        chroma_store=chroma,
        chunk_embedding_repository=FakeChunkEmbeddingRepository(),
        document_chunk_repository=FakeDocumentChunkRepository(),
        document_repository=FakeDocumentRepository(),
    )

    count = service.index_document(document_id)

    assert count == 1
    assert chroma.count_for_document(document_id) == 1
    assert chroma.records[document_id][0]["content"] == "Apply for leave via HR portal"
