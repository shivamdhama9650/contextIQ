import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.auth import AuthenticatedUser
from app.repositories.document_repository import DocumentRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.storage_repository import StorageRepository
from app.schemas.document import DocumentCategory, DocumentResponse, DocumentStatus
from app.services.document_parsing_service import DocumentParsingService

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DOCUMENT_BUCKET = "company-documents"
PDF_MIME_TYPE = "application/pdf"


@dataclass(frozen=True)
class UploadResult:
    document: DocumentResponse
    message: str


class DocumentUploadService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_repository: StorageRepository,
        profile_repository: ProfileRepository,
        parsing_service: DocumentParsingService,
    ) -> None:
        self.document_repository = document_repository
        self.storage_repository = storage_repository
        self.profile_repository = profile_repository
        self.parsing_service = parsing_service

    async def upload_document(
        self,
        file: UploadFile,
        category: DocumentCategory,
        current_user: AuthenticatedUser,
        description: str | None = None,
        *,
        process_immediately: bool = True,
    ) -> UploadResult:
        self._ensure_user_profile(current_user)

        content = await file.read()
        self._validate_pdf_upload(file=file, content=content)

        filename = self._sanitize_filename(file.filename or "document.pdf")
        document_id = str(uuid4())
        storage_path = f"{current_user.id}/{document_id}/{filename}"
        checksum = hashlib.sha256(content).hexdigest()
        title = (
            Path(filename).stem.replace("-", " ").replace("_", " ").strip()
            or "Uploaded document"
        )

        self.storage_repository.upload_pdf(
            bucket=DOCUMENT_BUCKET,
            path=storage_path,
            content=content,
        )

        try:
            record = self.document_repository.create(
                {
                    "id": document_id,
                    "owner_id": current_user.id,
                    "title": title,
                    "description": description,
                    "category": category.value,
                    "storage_bucket": DOCUMENT_BUCKET,
                    "storage_path": storage_path,
                    "mime_type": PDF_MIME_TYPE,
                    "file_size_bytes": len(content),
                    "checksum_sha256": checksum,
                    "status": DocumentStatus.uploaded.value,
                }
            )
        except Exception as exc:
            logger.exception("Document metadata insert failed for %s", document_id)
            self.storage_repository.delete_pdf(
                bucket=DOCUMENT_BUCKET,
                path=storage_path,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document metadata could not be saved. Upload was rolled back.",
            ) from exc

        logger.info(
            "Document uploaded",
            extra={
                "document_id": document_id,
                "owner_id": current_user.id,
                "category": category.value,
            },
        )

        if process_immediately:
            parsed_document = self.parsing_service.parse_and_persist(record, content)
            message = self._upload_message(parsed_document)
            return UploadResult(document=parsed_document, message=message)

        return UploadResult(
            document=DocumentResponse.model_validate(record),
            message="Document uploaded successfully. Processing has started in the background.",
        )

    def list_my_documents(self, current_user: AuthenticatedUser) -> list[DocumentResponse]:
        self._ensure_user_profile(current_user)
        records = self.document_repository.list_for_owner(current_user.id)
        return [DocumentResponse.model_validate(record) for record in records]

    def _ensure_user_profile(self, current_user: AuthenticatedUser) -> None:
        try:
            self.profile_repository.ensure_exists(current_user)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            logger.exception("Profile sync failed for user %s", current_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User profile could not be synchronized",
            ) from exc

    @staticmethod
    def _validate_pdf_upload(file: UploadFile, content: bytes) -> None:
        filename = file.filename or ""

        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported",
            )

        if file.content_type != PDF_MIME_TYPE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must use application/pdf content type",
            )

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 10 MB upload limit",
            )

        if not content.startswith(b"%PDF"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file does not look like a valid PDF",
            )

    @staticmethod
    def _upload_message(document: DocumentResponse) -> str:
        if document.status == DocumentStatus.ready:
            return "Document uploaded and indexed for semantic search."
        if document.status == DocumentStatus.failed:
            return (
                document.error_message
                or "Document uploaded but parsing failed. You can retry from the documents page."
            )
        return "Document uploaded successfully."

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        name = Path(filename).name.strip()
        name = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
        name = re.sub(r"-{2,}", "-", name).strip(".-")

        if not name:
            return "document.pdf"

        if not name.lower().endswith(".pdf"):
            return f"{name}.pdf"

        return name
