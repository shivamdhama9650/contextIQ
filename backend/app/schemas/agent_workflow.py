from pydantic import BaseModel, Field


class AgentWorkflowRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Employee question to route")


class AgentWorkflowResponse(BaseModel):
    query: str
    selected_agent: str
    agent_name: str
    answer: str
    sources: list[dict] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)

