from typing import Any
from .base import Agent


class HRAgent(Agent):
    """Handles HR-related queries: leave policies, benefits, holidays."""

    @property
    def name(self) -> str:
        return "HRAgent"

    def handle(self, message: str) -> dict[str, Any]:
        answer = (
            "Our leave policy grants 20 paid days per year, plus public holidays. "
            "Benefits include health insurance, 401k matching, and flexible working hours. "
            "To apply for leave, submit a request through the HR portal at least 3 days in advance."
        )
        return {"agent": self.name, "answer": answer}
