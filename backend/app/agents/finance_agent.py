from typing import Any
from .base import Agent


class FinanceAgent(Agent):
    """Handles reimbursements, expense policies, and general finance queries."""

    @property
    def name(self) -> str:
        return "FinanceAgent"

    def handle(self, message: str) -> dict[str, Any]:
        answer = (
            "Reimbursements must be submitted within 30 days of the expense using the Finance portal. "
            "Expense policy: meals capped at $50/day, travel at $200/day, hotel at $150/night. "
            "Attach receipts for all expenses above $25. "
            "Reimbursements are processed within 5-7 business days after manager approval."
        )
        return {"agent": self.name, "answer": answer}
