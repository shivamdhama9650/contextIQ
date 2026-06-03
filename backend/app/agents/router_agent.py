"""Deterministic router agent that delegates queries to specialist agents."""

from typing import Any

from app.agents.base import Agent
from app.agents.devops_agent import DevOpsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.hr_agent import HRAgent
from app.agents.report_agent import ReportAgent
from app.agents.security_agent import SecurityAgent


class RouterAgent(Agent):
    """Keyword-based router used before the LangGraph workflow is introduced."""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {
            "hr": HRAgent(),
            "devops": DevOpsAgent(),
            "security": SecurityAgent(),
            "finance": FinanceAgent(),
            "report": ReportAgent(),
        }
        self._keyword_map = {
            "hr": ["leave", "benefit", "holiday", "vacation", "pto"],
            "devops": ["ci", "cd", "docker", "kubernetes", "deployment", "pipeline"],
            "security": ["access", "permission", "password", "audit", "vulnerability"],
            "finance": ["reimburse", "expense", "invoice", "budget", "finance"],
            "report": ["summary", "report", "analytics", "dashboard"],
        }

    @property
    def name(self) -> str:
        return "RouterAgent"

    def _detect_agent(self, message: str) -> Agent:
        lowered = message.lower()
        for key, keywords in self._keyword_map.items():
            if any(word in lowered for word in keywords):
                return self._agents[key]
        return self._agents["hr"]

    def handle(self, message: str, user_id: str | None = None) -> dict[str, Any]:
        agent = self._detect_agent(message)
        response = agent.handle(message)
        response["routed_to"] = agent.name
        response["user_id"] = user_id
        return response

