from typing import Any

from supabase import Client

from app.core.auth import AuthenticatedUser


class ProfileRepository:
    def __init__(self, client: Client) -> None:
        self.client = client

    def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        response = (
            self.client.table("profiles")
            .select("*")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )

        if response.data is None:
            return None

        return dict(response.data)

    def upsert_from_auth_user(self, user: AuthenticatedUser) -> dict[str, Any]:
        if not user.email:
            raise ValueError("Authenticated user is missing an email claim")

        metadata = user.claims.get("user_metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        payload: dict[str, Any] = {
            "id": user.id,
            "email": user.email,
            "full_name": metadata.get("full_name") or metadata.get("name"),
            "avatar_url": metadata.get("avatar_url") or metadata.get("picture"),
        }

        response = self.client.table("profiles").upsert(payload, on_conflict="id").execute()

        if not response.data:
            raise RuntimeError("Profile record was not created")

        return dict(response.data[0])

    def ensure_exists(self, user: AuthenticatedUser) -> dict[str, Any]:
        existing = self.get_by_id(user.id)
        if existing is not None:
            return existing

        return self.upsert_from_auth_user(user)

    def list_profiles(self) -> list[dict[str, Any]]:
        response = (
            self.client.table("profiles")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return [dict(item) for item in response.data or []]

    def update_role(self, user_id: str, role: str) -> dict[str, Any]:
        response = (
            self.client.table("profiles")
            .update({"role": role})
            .eq("id", user_id)
            .select("*")
            .execute()
        )

        if not response.data:
            raise RuntimeError("Profile role could not be updated")

        return dict(response.data[0])
