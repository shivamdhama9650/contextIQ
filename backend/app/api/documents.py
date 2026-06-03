from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.config import settings
from app.core.rbac import ensure_can_manage_document_category, get_current_profile, require_admin
from app.db.supabase import get_supabase_admin_client
from app.repositories.document_repository import DocumentRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.storage_repository import StorageRepository
from app.schemas.document import (
    DocumentCategory,
    DocumentChunkResponse,
    DocumentDetailResponse,
    DocumentEmbedResponse,
    DocumentPageResponse,
    DocumentParseResponse,
    DocumentReprocessItem,
    DocumentReprocessResponse,
    DocumentResponse,
    DocumentStatus,
    DocumentUploadResponse,
)
from app.schemas.profile import AppRole, ProfileResponse
from app.schemas.search import VectorIndexResponse
from app.services.document_parsing_service import DocumentParsingService
from app.services.document_service import DocumentUploadService
from app.services.knowledge_pipeline import build_document_parsing_service

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_upload_service() -> DocumentUploadService:
    client = get_supabase_admin_client()
    return DocumentUploadService(
        document_repository=DocumentRepository(client),
        storage_repository=StorageRepository(client),
        profile_repository=ProfileRepository(client),
        parsing_service=build_document_parsing_service(client),
    )


def get_document_parsing_service() -> DocumentParsingService:
    return build_document_parsing_service(get_supabase_admin_client())


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    current_profile: Annotated[ProfileResponse, Depends(get_current_profile)],
    service: Annotated[DocumentUploadService, Depends(get_document_upload_service)],
    file: Annotated[UploadFile, File()],
    category: Annotated[DocumentCategory, Form()] = DocumentCategory.general,
    description: Annotated[str | None, Form()] = None,
) -> DocumentUploadResponse:
    if category != DocumentCategory.general or current_profile.role != AppRole.employee:
        ensure_can_manage_document_category(current_profile.role, category)

    result = await service.upload_document(
        file=file,
        category=category,
        description=description,
        current_user=current_user,
        process_immediately=False,
    )
    background_tasks.add_task(
        service.parsing_service.reprocess_by_id,
        str(result.document.id),
    )

    return DocumentUploadResponse(document=result.document, message=result.message)


@router.get("", response_model=list[DocumentResponse])
def list_my_documents(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[DocumentUploadService, Depends(get_document_upload_service)],
) -> list[DocumentResponse]:
    return service.list_my_documents(current_user)


@router.get("/admin/all", response_model=list[DocumentResponse])
def list_all_documents_for_admin(
    _: Annotated[ProfileResponse, Depends(require_admin)],
) -> list[DocumentResponse]:
    repository = DocumentRepository(get_supabase_admin_client())
    try:
        return [
            DocumentResponse.model_validate(document)
            for document in repository.list_all(limit=250)
        ]
    except Exception:
        if settings.app_env == "development":
            return []
        raise


@router.post("/admin/reprocess", response_model=DocumentReprocessResponse)
def reprocess_all_documents_for_admin(
    _: Annotated[ProfileResponse, Depends(require_admin)],
    parsing_service: Annotated[DocumentParsingService, Depends(get_document_parsing_service)],
) -> DocumentReprocessResponse:
    repository = DocumentRepository(get_supabase_admin_client())
    documents = repository.list_all(limit=250)
    results: list[DocumentReprocessItem] = []

    for document in documents:
        document_id = str(document["id"])
        try:
            processed = parsing_service.reprocess_by_id(document_id)
            results.append(
                DocumentReprocessItem(
                    document_id=processed.id,
                    title=processed.title,
                    status=processed.status,
                    message="Document parsed, embedded, and indexed.",
                )
            )
        except Exception as exc:
            results.append(
                DocumentReprocessItem(
                    document_id=document["id"],
                    title=str(document.get("title", "Untitled document")),
                    status=DocumentStatus.failed,
                    message=str(exc)[:300],
                )
            )

    return DocumentReprocessResponse(
        processed_count=len(results),
        documents=results,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_detail(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    parsing_service: Annotated[DocumentParsingService, Depends(get_document_parsing_service)],
) -> DocumentDetailResponse:
    document, pages, chunk_count, embedding_count, vector_count, embedding_model = (
        parsing_service.get_document_with_pages(
            document_id=str(document_id),
            owner_id=current_user.id,
        )
    )
    page_models = [DocumentPageResponse.model_validate(page) for page in pages]

    chunk_rows = parsing_service.get_chunks_for_document(
        document_id=str(document_id),
        owner_id=current_user.id,
        limit=20,
    )
    chunk_models = [DocumentChunkResponse.model_validate(chunk) for chunk in chunk_rows]

    return DocumentDetailResponse(
        document=document,
        page_count=len(page_models),
        chunk_count=chunk_count,
        embedding_count=embedding_count,
        vector_count=vector_count,
        embedding_model=embedding_model,
        pages=page_models,
        chunks=chunk_models,
    )


@router.post("/{document_id}/embed", response_model=DocumentEmbedResponse)
def embed_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    parsing_service: Annotated[DocumentParsingService, Depends(get_document_parsing_service)],
) -> DocumentEmbedResponse:
    count = parsing_service.embed_for_owner(
        document_id=str(document_id),
        owner_id=current_user.id,
    )
    return DocumentEmbedResponse(
        document_id=document_id,
        embedding_count=count,
        embedding_model=settings.embedding_model_name,
        message=f"Generated {count} embeddings and updated the vector index.",
    )


@router.post("/{document_id}/index", response_model=VectorIndexResponse)
def index_document_vectors(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    parsing_service: Annotated[DocumentParsingService, Depends(get_document_parsing_service)],
) -> VectorIndexResponse:
    count = parsing_service.index_for_owner(
        document_id=str(document_id),
        owner_id=current_user.id,
    )
    return VectorIndexResponse(
        document_id=str(document_id),
        vector_count=count,
        message=f"Indexed {count} vectors in ChromaDB.",
    )


@router.post("/{document_id}/parse", response_model=DocumentParseResponse)
def parse_document(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    parsing_service: Annotated[DocumentParsingService, Depends(get_document_parsing_service)],
) -> DocumentParseResponse:
    document = parsing_service.parse_for_owner(
        document_id=str(document_id),
        owner_id=current_user.id,
    )
    message = (
        "Document parsed, embedded, and indexed for semantic search."
        if document.status.value == "ready"
        else document.error_message or "Document processing failed."
    )
    return DocumentParseResponse(document=document, message=message)
