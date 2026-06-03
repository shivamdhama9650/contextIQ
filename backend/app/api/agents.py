from typing import Annotated

from fastapi import APIRouter, Depends

from app.agents.langgraph_workflow import LangGraphAgentWorkflow
from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.agent_workflow import AgentWorkflowRequest, AgentWorkflowResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])


def get_agent_workflow() -> LangGraphAgentWorkflow:
    return LangGraphAgentWorkflow()


@router.post("/workflow", response_model=AgentWorkflowResponse)
def run_agent_workflow(
    payload: AgentWorkflowRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    workflow: Annotated[LangGraphAgentWorkflow, Depends(get_agent_workflow)],
) -> AgentWorkflowResponse:
    result = workflow.invoke(query=payload.query, user_id=current_user.id)

    return AgentWorkflowResponse(
        query=result["query"],
        selected_agent=result["selected_agent"],
        agent_name=result["agent_name"],
        answer=result["answer"],
        sources=result.get("sources", []),
        trace=result.get("trace", []),
    )

