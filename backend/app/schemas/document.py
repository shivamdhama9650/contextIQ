from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentCategory(StrEnum):
    hr = "hr"
    devops = "devops"
    security = "security"
    finance = "finance"
    technical = "technical"
    general = "general"


class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"
    archived = "archived"


class DocumentResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: str | None = None
    category: DocumentCategory
    storage_bucket: str
    storage_path: str
    mime_type: str
    file_size_bytes: int = Field(gt=0)
    checksum_sha256: str | None = None
    status: DocumentStatus
    error_message: str | None = None
    uploaded_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    message: str


class DocumentPageResponse(BaseModel):
    id: UUID
    document_id: UUID
    page_number: int = Field(gt=0)
    text_content: str
    metadata: dict[str, object]
    created_at: datetime


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    page_id: UUID | None = None
    chunk_index: int = Field(ge=0)
    content: str
    token_count: int | None = None
    page_start: int | None = Field(default=None, gt=0)
    page_end: int | None = Field(default=None, gt=0)
    metadata: dict[str, object]
    created_at: datetime


class DocumentDetailResponse(BaseModel):
    document: DocumentResponse
    page_count: int
    chunk_count: int
    embedding_count: int = 0
    vector_count: int = 0
    embedding_model: str | None = None
    pages: list[DocumentPageResponse]
    chunks: list[DocumentChunkResponse] = []


class DocumentEmbedResponse(BaseModel):
    document_id: UUID
    embedding_count: int
    embedding_model: str
    message: str


class DocumentParseResponse(BaseModel):
    document: DocumentResponse
    message: str


class DocumentReprocessItem(BaseModel):
    document_id: UUID
    title: str
    status: DocumentStatus
    message: str


class DocumentReprocessResponse(BaseModel):
    processed_count: int = Field(ge=0)
    documents: list[DocumentReprocessItem]
