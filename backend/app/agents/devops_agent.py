"""DevOps specialist agent."""

from typing import Any

from app.agents.base import Agent


class DevOpsAgent(Agent):
    """Handles CI/CD, Docker, Kubernetes, and deployment questions."""

    @property
    def name(self) -> str:
        return "DevOpsAgent"

    def handle(self, message: str) -> dict[str, Any]:
        return {
            "agent": self.name,
            "answer": (
                "I routed this to DevOps. Use deployment guides, CI/CD runbooks, "
                "Docker documentation, and Kubernetes SOPs as the source of truth."
            ),
            "query": message,
        }

