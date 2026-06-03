from typing import Any

from supabase import Client


class DocumentPageRepository:
    def __init__(self, client: Client) -> None:
        self.client = client

    def delete_for_document(self, document_id: str) -> None:
        self.client.table("document_pages").delete().eq("document_id", document_id).execute()

    def insert_many(self, document_id: str, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not pages:
            return []

        payload = [{"document_id": document_id, **page} for page in pages]
        response = self.client.table("document_pages").insert(payload).execute()
        return [dict(item) for item in response.data or []]

    def list_for_document(self, document_id: str) -> list[dict[str, Any]]:
        response = (
            self.client.table("document_pages")
            .select("*")
            .eq("document_id", document_id)
            .order("page_number")
            .execute()
        )
        return [dict(item) for item in response.data or []]

    def count_for_document(self, document_id: str) -> int:
        response = (
            self.client.table("document_pages")
            .select("id", count="exact")
            .eq("document_id", document_id)
            .execute()
        )
        return response.count or 0
