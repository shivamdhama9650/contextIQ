from typing import Any


class Agent:
    """Base class for all specialist agents."""

    @property
    def name(self) -> str:
        """Human-readable agent name."""
        raise NotImplementedError

    def handle(self, message: str) -> dict[str, Any]:
        """Process a user message and return a JSON-serializable response."""
        raise NotImplementedError
