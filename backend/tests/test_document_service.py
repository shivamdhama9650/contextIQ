from datetime import UTC, datetime
from io import BytesIO
from uuid import uuid4

import pytest
from fastapi import HTTPException, UploadFile

from app.core.auth import AuthenticatedUser
from app.schemas.document import DocumentCategory, DocumentStatus
from app.services.document_service import DocumentUploadService


class FakeDocumentRepository:
    def __init__(self, *, fail_on_create: bool = False) -> None:
        self.created_payload: dict | None = None
        self.fail_on_create = fail_on_create

    def create(self, payload: dict) -> dict:
        self.created_payload = payload
        if self.fail_on_create:
            raise RuntimeError("database unavailable")

        now = datetime.now(UTC).isoformat()
        return {
            **payload,
            "uploaded_at": now,
            "updated_at": now,
        }

    def list_for_owner(self, owner_id: str) -> list[dict]:
        return []


class FakeStorageRepository:
    def __init__(self) -> None:
        self.uploaded_path: str | None = None
        self.uploaded_content: bytes | None = None
        self.deleted_paths: list[str] = []

    def upload_pdf(self, bucket: str, path: str, content: bytes) -> None:
        self.uploaded_path = path
        self.uploaded_content = content

    def delete_pdf(self, bucket: str, path: str) -> None:
        self.deleted_paths.append(path)


class FakeProfileRepository:
    def __init__(self) -> None:
        self.ensure_calls = 0

    def ensure_exists(self, user: AuthenticatedUser) -> dict:
        self.ensure_calls += 1
        return {
            "id": user.id,
            "email": user.email or "user@example.com",
            "role": "employee",
            "is_active": True,
        }


class FakeParsingService:
    def parse_and_persist(self, document: dict, content: bytes):
        from app.schemas.document import DocumentResponse

        return DocumentResponse.model_validate(
            {
                **document,
                "status": DocumentStatus.ready.value,
                "error_message": None,
            }
        )


def make_upload_file(filename: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
        headers={"content-type": content_type},
    )


def make_service(
    *,
    fail_on_create: bool = False,
) -> tuple[
    DocumentUploadService,
    FakeDocumentRepository,
    FakeStorageRepository,
    FakeProfileRepository,
]:
    document_repository = FakeDocumentRepository(fail_on_create=fail_on_create)
    storage_repository = FakeStorageRepository()
    profile_repository = FakeProfileRepository()
    service = DocumentUploadService(
        document_repository=document_repository,
        storage_repository=storage_repository,
        profile_repository=profile_repository,
        parsing_service=FakeParsingService(),
    )
    return service, document_repository, storage_repository, profile_repository


@pytest.mark.anyio
async def test_upload_document_validates_and_creates_metadata() -> None:
    service, document_repository, storage_repository, profile_repository = make_service()
    user_id = str(uuid4())
    user = AuthenticatedUser(id=user_id, email="user@example.com", claims={})
    file = make_upload_file("Leave Policy.pdf", b"%PDF-1.7 content", "application/pdf")

    result = await service.upload_document(
        file=file,
        category=DocumentCategory.hr,
        current_user=user,
    )

    assert profile_repository.ensure_calls == 1
    assert str(result.document.owner_id) == user_id
    assert result.document.category == DocumentCategory.hr
    assert result.document.storage_bucket == "company-documents"
    assert storage_repository.uploaded_path is not None
    assert storage_repository.uploaded_path.startswith(f"{user_id}/")
    assert storage_repository.uploaded_content == b"%PDF-1.7 content"
    assert document_repository.created_payload is not None
    assert document_repository.created_payload["title"] == "Leave Policy"


@pytest.mark.anyio
async def test_upload_document_rolls_back_storage_when_metadata_insert_fails() -> None:
    service, _, storage_repository, _ = make_service(fail_on_create=True)
    user = AuthenticatedUser(id=str(uuid4()), email="user@example.com", claims={})
    file = make_upload_file("policy.pdf", b"%PDF-1.7 content", "application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await service.upload_document(
            file=file,
            category=DocumentCategory.general,
            current_user=user,
        )

    assert exc_info.value.status_code == 500
    assert storage_repository.uploaded_path is not None
    assert storage_repository.deleted_paths == [storage_repository.uploaded_path]


@pytest.mark.anyio
async def test_upload_document_rejects_non_pdf_extension() -> None:
    service, _, _, _ = make_service()
    user = AuthenticatedUser(id=str(uuid4()), email="user@example.com", claims={})
    file = make_upload_file("policy.txt", b"%PDF-1.7 content", "application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await service.upload_document(
            file=file,
            category=DocumentCategory.general,
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Only PDF files are supported"


@pytest.mark.anyio
async def test_upload_document_rejects_fake_pdf_content() -> None:
    service, _, _, _ = make_service()
    user = AuthenticatedUser(id=str(uuid4()), email="user@example.com", claims={})
    file = make_upload_file("policy.pdf", b"not really a pdf", "application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await service.upload_document(
            file=file,
            category=DocumentCategory.general,
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Uploaded file does not look like a valid PDF"
