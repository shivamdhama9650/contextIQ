import json
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.query import QueryRequest
from app.services.knowledge_pipeline import build_rag_service
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/chat", tags=["chat"])


def get_rag_service() -> RAGService:
    return build_rag_service()


async def stream_chat_events(
    rag: RAGService,
    request: QueryRequest,
    current_user: AuthenticatedUser,
) -> AsyncGenerator[dict[str, str], None]:
    async for event in rag.stream_answer(
        request.query,
        k=request.k or 5,
        owner_id=current_user.id,
    ):
        event_type = event.get("type", "token")
        payload = {key: value for key, value in event.items() if key != "type"}
        yield {
            "event": str(event_type),
            "data": json.dumps(payload),
        }


@router.post("")
async def chat_endpoint(
    request: QueryRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    rag: Annotated[RAGService, Depends(get_rag_service)],
) -> EventSourceResponse:
    try:
        return EventSourceResponse(
            stream_chat_events(rag=rag, request=request, current_user=current_user),
            media_type="text/event-stream",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

