"""Chat API endpoint.

Routes user queries through the RouterAgent which delegates to the
appropriate specialist (HR, DevOps, Security, Finance, Report).
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.agents.router_agent import RouterAgent
from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.query import QueryRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Single shared instance – agents are stateless so this is thread-safe
_router_agent = RouterAgent()


@router.post("")
async def chat_endpoint(
    request: QueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> JSONResponse:
    """Route the user query to the appropriate domain specialist agent.

    Returns JSON containing:
    - ``answer``: the specialist's response text
    - ``agent``: the specialist agent that handled the query
    - ``routed_to``: same as ``agent`` (for debugging)
    - ``user_id``: the authenticated user's ID
    """
    try:
        response = _router_agent.handle(request.query, user_id=current_user.id)
        return JSONResponse(content=response)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
