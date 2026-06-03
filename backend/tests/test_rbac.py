import asyncio

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.documents import get_document_upload_service
from app.core.rbac import (
    can_manage_document_category,
    get_current_profile,
    get_profile_repository,
    require_admin,
    require_roles,
)
from app.main import app
from app.schemas.document import DocumentCategory, DocumentResponse, DocumentStatus
from app.schemas.profile import AppRole, ProfileResponse

client = TestClient(app)


class FakeProfileRepository:
    def __init__(self) -> None:
        self.updated_role: str | None = None

    def list_profiles(self) -> list[dict]:
        return [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "email": "admin@example.com",
                "role": "admin",
                "is_active": True,
            }
        ]

    def update_role(self, user_id: str, role: str) -> dict:
        self.updated_role = role
        return {
            "id": user_id,
            "email": "employee@example.com",
            "role": role,
            "is_active": True,
        }


class FakeUploadService:
    def __init__(self) -> None:
        self.process_immediately: bool | None = None
        self.parsing_service = self
        self.reprocessed: list[str] = []

    async def upload_document(
        self,
        *,
        file,
        category,
        current_user,
        description=None,
        process_immediately=True,
    ):
        from app.services.document_service import UploadResult

        self.process_immediately = process_immediately
        document = DocumentResponse(
            id="00000000-0000-0000-0000-000000000010",
            owner_id=current_user.id,
            title="Policy",
            description=description,
            category=category,
            storage_bucket="company-documents",
            storage_path="policy.pdf",
            mime_type="application/pdf",
            file_size_bytes=18,
            checksum_sha256=None,
            status=DocumentStatus.uploaded,
            error_message=None,
            uploaded_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        return UploadResult(
            document=document,
            message="Document uploaded successfully. Processing has started in the background.",
        )

    def reprocess_by_id(self, document_id: str) -> None:
        self.reprocessed.append(document_id)


def make_profile(role: AppRole) -> ProfileResponse:
    return ProfileResponse(
        id="00000000-0000-0000-0000-000000000001",
        email="user@example.com",
        role=role,
        is_active=True,
    )


def test_category_manager_permissions() -> None:
    assert can_manage_document_category(AppRole.hr_admin, DocumentCategory.hr)
    assert can_manage_document_category(AppRole.admin, DocumentCategory.finance)
    assert not can_manage_document_category(AppRole.employee, DocumentCategory.hr)


def test_require_roles_rejects_missing_role() -> None:
    dependency = require_roles(AppRole.admin)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(dependency(make_profile(AppRole.employee)))

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient role permissions"


def test_admin_can_update_profile_role() -> None:
    fake_repository = FakeProfileRepository()

    app.dependency_overrides[require_admin] = lambda: make_profile(AppRole.admin)
    app.dependency_overrides[get_profile_repository] = lambda: fake_repository

    try:
        response = client.patch(
            "/auth/profiles/00000000-0000-0000-0000-000000000002/role",
            json={"role": "finance_admin"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["role"] == "finance_admin"
    assert fake_repository.updated_role == "finance_admin"


def test_employee_cannot_upload_hr_document() -> None:
    app.dependency_overrides[get_current_profile] = lambda: make_profile(AppRole.employee)

    # Keep the endpoint dependency graph lightweight; permission should fail before service use.
    app.dependency_overrides[get_document_upload_service] = lambda: object()

    try:
        response = client.post(
            "/documents/upload",
            data={"category": "hr"},
            files={"file": ("policy.pdf", b"%PDF-1.7 content", "application/pdf")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_upload_endpoint_defers_processing() -> None:
    fake_service = FakeUploadService()

    app.dependency_overrides[get_current_profile] = lambda: make_profile(AppRole.employee)
    app.dependency_overrides[get_document_upload_service] = lambda: fake_service

    try:
        response = client.post(
            "/documents/upload",
            data={"category": "general"},
            files={"file": ("policy.pdf", b"%PDF-1.7 content", "application/pdf")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["document"]["status"] == "uploaded"
    assert fake_service.process_immediately is False
    assert fake_service.reprocessed == ["00000000-0000-0000-0000-000000000010"]
