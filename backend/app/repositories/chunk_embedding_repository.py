from typing import Any

from supabase import Client


class ChunkEmbeddingRepository:
    def __init__(self, client: Client) -> None:
        self.client = client

    def delete_for_document(self, document_id: str) -> None:
        self.client.table("chunk_embeddings").delete().eq("document_id", document_id).execute()

    def insert_many(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            return []

        response = self.client.table("chunk_embeddings").insert(rows).execute()
        return [dict(item) for item in response.data or []]

    def count_for_document(self, document_id: str) -> int:
        response = (
            self.client.table("chunk_embeddings")
            .select("id", count="exact")
            .eq("document_id", document_id)
            .execute()
        )
        return response.count or 0

    def list_for_document(self, document_id: str) -> list[dict[str, Any]]:
        response = (
            self.client.table("chunk_embeddings")
            .select("*")
            .eq("document_id", document_id)
            .execute()
        )
        return [dict(item) for item in response.data or []]

    def get_model_name_for_document(self, document_id: str) -> str | None:
        response = (
            self.client.table("chunk_embeddings")
            .select("model_name")
            .eq("document_id", document_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return str(response.data[0]["model_name"])
