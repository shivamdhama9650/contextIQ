from fastapi.testclient import TestClient

from app.agents.langgraph_workflow import LangGraphAgentWorkflow
from app.main import app

client = TestClient(app)


def test_langgraph_workflow_routes_security_question() -> None:
    workflow = LangGraphAgentWorkflow()

    result = workflow.invoke(
        query="What are the password requirements?",
        user_id="user-123",
    )

    assert result["selected_agent"] == "security"
    assert result["agent_name"] == "SecurityAgent"
    assert "router:selected:security" in result["trace"]
    assert "specialist:executed:SecurityAgent" in result["trace"]


def test_langgraph_workflow_api_returns_agent_trace() -> None:
    response = client.post(
        "/api/agents/workflow",
        json={"query": "How do I submit reimbursement requests?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_agent"] == "finance"
    assert payload["agent_name"] == "FinanceAgent"
    assert payload["trace"] == [
        "router:selected:finance",
        "specialist:executed:FinanceAgent",
    ]

