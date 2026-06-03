"""Security specialist agent."""

from typing import Any

from app.agents.base import Agent


class SecurityAgent(Agent):
    """Handles access control, security policy, and audit questions."""

    @property
    def name(self) -> str:
        return "SecurityAgent"

    def handle(self, message: str) -> dict[str, Any]:
        return {
            "agent": self.name,
            "answer": (
                "I routed this to Security. Use uploaded security policies, access "
                "control standards, and audit procedures as the source of truth."
            ),
            "query": message,
        }

