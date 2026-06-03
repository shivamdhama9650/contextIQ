"""HR specialist agent."""

from typing import Any

from app.agents.base import Agent


class HRAgent(Agent):
    """Handles leave policies, benefits, holidays, and HR policy questions."""

    @property
    def name(self) -> str:
        return "HRAgent"

    def handle(self, message: str) -> dict[str, Any]:
        return {
            "agent": self.name,
            "answer": (
                "I routed this to HR. Use uploaded HR policy documents as the "
                "source of truth for leave, benefits, holidays, and workplace policy."
            ),
            "query": message,
        }

