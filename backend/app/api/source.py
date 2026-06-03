from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import AuthenticatedUser, get_current_user
from app.db.supabase import get_supabase_admin_client
from app.schemas.source import SourceDetailResponse
from app.services.document_parsing_service import DocumentParsingService
from app.services.knowledge_pipeline import build_document_parsing_service

router = APIRouter(prefix="/api/source", tags=["source"])


def get_parsing_service() -> DocumentParsingService:
    return build_document_parsing_service(get_supabase_admin_client())


@router.get("/{document_id}", response_model=SourceDetailResponse)
async def get_source_detail(
    document_id: str,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    parsing_service: Annotated[DocumentParsingService, Depends(get_parsing_service)],
) -> SourceDetailResponse:
    try:
        doc_response, pages, _, _, _, _ = parsing_service.get_document_with_pages(
            document_id=document_id,
            owner_id=current_user.id,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document details",
        ) from exc

    preview = ""
    if pages:
        preview = pages[0].get("text_content", "")[:500]

    return SourceDetailResponse(
        document_id=document_id,
        title=doc_response.title,
        preview=preview,
    )

