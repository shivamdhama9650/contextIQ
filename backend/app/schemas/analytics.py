from pydantic import BaseModel, Field

from app.schemas.document import DocumentResponse


class AnalyticsBreakdownItem(BaseModel):
    label: str
    count: int = Field(ge=0)
    percentage: float = Field(ge=0, le=100)


class AnalyticsOverviewResponse(BaseModel):
    total_users: int = Field(ge=0)
    active_users: int = Field(ge=0)
    inactive_users: int = Field(ge=0)
    total_documents: int = Field(ge=0)
    ready_documents: int = Field(ge=0)
    failed_documents: int = Field(ge=0)
    processing_documents: int = Field(ge=0)
    uploaded_documents: int = Field(ge=0)
    archived_documents: int = Field(ge=0)
    total_storage_bytes: int = Field(ge=0)
    total_chunks: int = Field(ge=0)
    total_embeddings: int = Field(ge=0)
    readiness_rate: float = Field(ge=0, le=100)
    category_breakdown: list[AnalyticsBreakdownItem]
    status_breakdown: list[AnalyticsBreakdownItem]
    role_breakdown: list[AnalyticsBreakdownItem]
    recent_documents: list[DocumentResponse]
