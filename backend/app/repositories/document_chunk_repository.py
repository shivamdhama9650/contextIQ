from typing import Any

from supabase import Client


class DocumentChunkRepository:
    def __init__(self, client: Client) -> None:
        self.client = client

    def delete_for_document(self, document_id: str) -> None:
        self.client.table("document_chunks").delete().eq("document_id", document_id).execute()

    def insert_many(self, document_id: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not chunks:
            return []

        payload = [{"document_id": document_id, **chunk} for chunk in chunks]
        response = self.client.table("document_chunks").insert(payload).execute()
        return [dict(item) for item in response.data or []]

    def list_for_document(self, document_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
        response = (
            self.client.table("document_chunks")
            .select("*")
            .eq("document_id", document_id)
            .order("chunk_index")
            .limit(limit)
            .execute()
        )
        return [dict(item) for item in response.data or []]

    def count_for_document(self, document_id: str) -> int:
        response = (
            self.client.table("document_chunks")
            .select("id", count="exact")
            .eq("document_id", document_id)
            .execute()
        )
        return response.count or 0
