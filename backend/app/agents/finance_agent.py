"""Finance specialist agent."""

from typing import Any

from app.agents.base import Agent


class FinanceAgent(Agent):
    """Handles reimbursements, expenses, procurement, and finance policies."""

    @property
    def name(self) -> str:
        return "FinanceAgent"

    def handle(self, message: str) -> dict[str, Any]:
        return {
            "agent": self.name,
            "answer": (
                "I routed this to Finance. Use reimbursement policies, finance SOPs, "
                "expense limits, and approval workflows as the source of truth."
            ),
            "query": message,
        }

