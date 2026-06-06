from typing import Any

from .base import Agent
from .devops_agent import DevOpsAgent
from .finance_agent import FinanceAgent
from .hr_agent import HRAgent
from .report_agent import ReportAgent
from .security_agent import SecurityAgent


class RouterAgent(Agent):
    """Deterministic router that delegates queries to specialist agents.

    Uses keyword matching to decide which specialist handles the query.
    In production, replace keyword matching with an LLM-based intent classifier.
    """

    @property
    def name(self) -> str:
        return "RouterAgent"

    def __init__(self) -> None:
        # Instantiate specialist agents once at startup
        self._agents: dict[str, Agent] = {
            "hr": HRAgent(),
            "devops": DevOpsAgent(),
            "security": SecurityAgent(),
            "finance": FinanceAgent(),
            "report": ReportAgent(),
        }
        # Map keyword sets to agent keys (order matters — first match wins)
        self._keyword_map: dict[str, list[str]] = {
            "hr": ["leave", "benefit", "holiday", "vacation", "hr", "salary", "appraisal"],
            "devops": ["ci", "cd", "docker", "kubernetes", "deployment", "pipeline", "git", "jenkins"],
            "security": ["access", "permission", "audit", "vulnerability", "password", "firewall", "vpn"],
            "finance": ["reimburse", "expense", "invoice", "budget", "finance", "reimbursement", "travel"],
            "report": ["summary", "report", "analytics", "dashboard", "statistics", "overview"],
        }

    def _detect_agent(self, message: str) -> Agent:
        """Return the best specialist agent based on keyword matching."""
        lowered = message.lower()
        for key, keywords in self._keyword_map.items():
            if any(word in lowered for word in keywords):
                return self._agents[key]
        # Default fallback to HR agent
        return self._agents["hr"]

    def handle(self, message: str, user_id: str | None = None) -> dict[str, Any]:
        """Route the message to the correct specialist and return the response.

        Adds 'routed_to' and 'user_id' fields for observability and audit.
        """
        agent = self._detect_agent(message)
        response = agent.handle(message)
        response["routed_to"] = agent.name
        response["user_id"] = user_id
        return response
