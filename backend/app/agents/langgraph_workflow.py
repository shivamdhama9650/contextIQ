"""LangGraph multi-agent workflow for enterprise knowledge routing."""

from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.base import Agent
from app.agents.devops_agent import DevOpsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.hr_agent import HRAgent
from app.agents.report_agent import ReportAgent
from app.agents.security_agent import SecurityAgent

AgentKey = Literal["hr", "devops", "security", "finance", "report"]


class AgentWorkflowState(TypedDict, total=False):
    query: str
    user_id: str | None
    selected_agent: AgentKey
    answer: str
    agent_name: str
    sources: list[dict[str, Any]]
    trace: list[str]


class LangGraphAgentWorkflow:
    """Routes a query through a LangGraph router and specialist node."""

    def __init__(self) -> None:
        self._agents: dict[AgentKey, Agent] = {
            "hr": HRAgent(),
            "devops": DevOpsAgent(),
            "security": SecurityAgent(),
            "finance": FinanceAgent(),
            "report": ReportAgent(),
        }
        self._keyword_map: dict[AgentKey, list[str]] = {
            "hr": ["leave", "benefit", "holiday", "vacation", "pto"],
            "devops": ["ci", "cd", "docker", "kubernetes", "deployment", "pipeline"],
            "security": ["access", "permission", "password", "audit", "vulnerability"],
            "finance": ["reimburse", "expense", "invoice", "budget", "finance"],
            "report": ["summary", "report", "analytics", "dashboard"],
        }
        self.graph = self._build_graph()

    def invoke(self, query: str, user_id: str | None = None) -> AgentWorkflowState:
        initial_state: AgentWorkflowState = {
            "query": query,
            "user_id": user_id,
            "trace": [],
            "sources": [],
        }
        return self.graph.invoke(initial_state)

    def _build_graph(self):
        workflow = StateGraph(AgentWorkflowState)

        workflow.add_node("router", self._route_node)
        workflow.add_node("hr_agent", self._specialist_node("hr"))
        workflow.add_node("devops_agent", self._specialist_node("devops"))
        workflow.add_node("security_agent", self._specialist_node("security"))
        workflow.add_node("finance_agent", self._specialist_node("finance"))
        workflow.add_node("report_agent", self._specialist_node("report"))

        workflow.add_edge(START, "router")
        workflow.add_conditional_edges(
            "router",
            self._route_condition,
            {
                "hr": "hr_agent",
                "devops": "devops_agent",
                "security": "security_agent",
                "finance": "finance_agent",
                "report": "report_agent",
            },
        )

        workflow.add_edge("hr_agent", END)
        workflow.add_edge("devops_agent", END)
        workflow.add_edge("security_agent", END)
        workflow.add_edge("finance_agent", END)
        workflow.add_edge("report_agent", END)

        return workflow.compile()

    def _route_node(self, state: AgentWorkflowState) -> AgentWorkflowState:
        selected_agent = self._detect_agent(state["query"])
        trace = [*state.get("trace", []), f"router:selected:{selected_agent}"]

        return {
            **state,
            "selected_agent": selected_agent,
            "trace": trace,
        }

    def _route_condition(self, state: AgentWorkflowState) -> AgentKey:
        return state.get("selected_agent", "hr")

    def _detect_agent(self, query: str) -> AgentKey:
        lowered = query.lower()
        for agent_key, keywords in self._keyword_map.items():
            if any(keyword in lowered for keyword in keywords):
                return agent_key
        return "hr"

    def _specialist_node(self, agent_key: AgentKey):
        def run_specialist(state: AgentWorkflowState) -> AgentWorkflowState:
            agent = self._agents[agent_key]
            response = agent.handle(state["query"])
            trace = [*state.get("trace", []), f"specialist:executed:{agent.name}"]

            return {
                **state,
                "agent_name": agent.name,
                "answer": str(response.get("answer", "")),
                "sources": list(response.get("sources", [])),
                "trace": trace,
            }

        return run_specialist

