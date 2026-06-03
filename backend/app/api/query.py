from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.query import QueryRequest, QueryResponse, Source
from app.services.knowledge_pipeline import build_rag_service
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/query", tags=["query"])


def get_rag_service() -> RAGService:
    return build_rag_service()


@router.post("", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    rag: Annotated[RAGService, Depends(get_rag_service)],
) -> QueryResponse:
    try:
        answer, sources = rag.answer_query(
            request.query,
            k=request.k or 5,
            owner_id=current_user.id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    source_models = [Source(**source) for source in sources]
    return QueryResponse(answer=answer, sources=source_models)

