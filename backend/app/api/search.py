from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.search import SearchHitResponse, SearchRequest, SearchResponse
from app.services.knowledge_pipeline import build_semantic_search_service

router = APIRouter(prefix="/search", tags=["search"])


def get_search_service():
    return build_semantic_search_service()


@router.post("", response_model=SearchResponse)
def semantic_search(
    payload: SearchRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    search_service: Annotated[object, Depends(get_search_service)],
) -> SearchResponse:
    hits = search_service.search_for_owner(
        query=payload.query,
        owner_id=current_user.id,
        limit=payload.limit,
    )

    return SearchResponse(
        query=payload.query,
        results=[
            SearchHitResponse(
                chunk_id=hit.chunk_id,
                document_id=hit.document_id,
                document_title=hit.document_title,
                category=hit.category,
                content=hit.content,
                page_start=hit.page_start,
                page_end=hit.page_end,
                relevance_score=hit.relevance_score,
            )
            for hit in hits
        ],
    )
