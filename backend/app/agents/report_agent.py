from typing import Any
from .base import Agent


class ReportAgent(Agent):
    """Generates summaries and reports based on user queries."""

    @property
    def name(self) -> str:
        return "ReportAgent"

    def handle(self, message: str) -> dict[str, Any]:
        answer = (
            "I can generate summaries and reports from your company documents. "
            "Please specify the document or topic you want summarized. "
            f"Your request: '{message}' - I will search through all available documents "
            "and compile a comprehensive summary for you."
        )
        return {"agent": self.name, "answer": answer}
