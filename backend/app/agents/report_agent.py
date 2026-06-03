"""Report specialist agent."""

from typing import Any

from app.agents.base import Agent


class ReportAgent(Agent):
    """Handles summaries, structured reports, and analytics-style questions."""

    @property
    def name(self) -> str:
        return "ReportAgent"

    def handle(self, message: str) -> dict[str, Any]:
        return {
            "agent": self.name,
            "answer": (
                "I routed this to Report. Use retrieved document evidence to produce "
                "summaries, reports, and structured analysis."
            ),
            "query": message,
            "sources": [],
        }

