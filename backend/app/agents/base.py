"""Base interfaces for deterministic specialist agents."""

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Base class for all specialist agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""
        raise NotImplementedError

    @abstractmethod
    def handle(self, message: str) -> dict[str, Any]:
        """Process a user message and return a JSON-serializable response."""
        raise NotImplementedError

