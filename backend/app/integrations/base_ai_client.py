"""
Base AI Client Interface

Provider-agnostic interface for all AI backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAIClient(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if provider is configured."""
        ...

    @abstractmethod
    async def generate_response(
        self,
        message: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Generate text response."""
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Return provider health."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Current model."""
        ...
