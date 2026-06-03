from typing import Any

from supabase import Client

from app.schemas.document import DocumentStatus


class DocumentRepository:
    def __init__(self, client: Client) -> None:
        self.client = client

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table("documents").insert(payload).execute()

        if not response.data:
            raise RuntimeError("Document metadata was not created")

        return dict(response.data[0])

    def get_by_id(self, document_id: str) -> dict[str, Any] | None:
        response = (
            self.client.table("documents")
            .select("*")
            .eq("id", document_id)
            .maybe_single()
            .execute()
        )

        if response.data is None:
            return None

        return dict(response.data)

    def get_for_owner(self, document_id: str, owner_id: str) -> dict[str, Any] | None:
        response = (
            self.client.table("documents")
            .select("*")
            .eq("id", document_id)
            .eq("owner_id", owner_id)
            .maybe_single()
            .execute()
        )

        if response.data is None:
            return None

        return dict(response.data)

    def list_for_owner(self, owner_id: str) -> list[dict[str, Any]]:
        response = (
            self.client.table("documents")
            .select("*")
            .eq("owner_id", owner_id)
            .order("uploaded_at", desc=True)
            .execute()
        )

        return [dict(item) for item in response.data or []]

    def list_all(self, *, limit: int = 100) -> list[dict[str, Any]]:
        response = (
            self.client.table("documents")
            .select("*")
            .order("uploaded_at", desc=True)
            .limit(limit)
            .execute()
        )

        return [dict(item) for item in response.data or []]

    def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        *,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"status": status.value}
        if error_message is not None:
            payload["error_message"] = error_message
        elif status != DocumentStatus.failed:
            payload["error_message"] = None

        response = (
            self.client.table("documents")
            .update(payload)
            .eq("id", document_id)
            .select("*")
            .execute()
        )

        if not response.data:
            raise RuntimeError(f"Document {document_id} could not be updated")

        return dict(response.data[0])
