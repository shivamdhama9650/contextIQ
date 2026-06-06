from typing import Any
from .base import Agent


class SecurityAgent(Agent):
    """Handles access control, security policies, and audit queries."""

    @property
    def name(self) -> str:
        return "SecurityAgent"

    def handle(self, message: str) -> dict[str, Any]:
        answer = (
            "All data is encrypted at rest (AES-256) and in transit (TLS 1.3). "
            "We enforce least-privilege IAM roles and conduct quarterly security audits. "
            "Password requirements: minimum 12 characters, uppercase, lowercase, number, and symbol. "
            "Access requests must be submitted through the IT portal with manager approval."
        )
        return {"agent": self.name, "answer": answer}
