"""Base guardrail interface for AgentGuard."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    """Result from guardrail evaluation."""

    passed: bool = Field(..., description="Whether the guardrail passed")
    action: str = Field(..., description="Action to take: allow, block, redact, mask, transform")
    reason: str = Field(..., description="Reason for the decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    risk_score: int = Field(default=0, ge=0, le=100, description="Risk score 0-100")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def is_passed(self) -> bool:
        """Check if guardrail passed."""
        return self.passed

    def should_block(self) -> bool:
        """Check if action should be blocked."""
        return self.action == "block"

    def get_risk_score(self) -> int:
        """Get risk score."""
        return self.risk_score


class Guardrail(ABC):
    """Base class for all guardrails."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize guardrail.

        Args:
            config: Configuration dictionary
        """
        config = config or {}
        self.name = config.get("name", self.__class__.__name__)
        self.enabled = config.get("enabled", True)
        self.config = config

    @abstractmethod
    async def evaluate(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """Evaluate input against this guardrail.

        Args:
            input_data: Input to evaluate
            context: Execution context

        Returns:
            GuardrailResult with evaluation outcome
        """
        pass

    def configure(self, config: Dict[str, Any]) -> None:
        """Update guardrail configuration.

        Args:
            config: New configuration values
        """
        self.config.update(config)
        if "enabled" in config:
            self.enabled = config["enabled"]

    def get_metadata(self) -> Dict[str, Any]:
        """Get guardrail metadata.

        Returns:
            Dictionary with metadata
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "version": self.config.get("version", "1.0.0"),
            "description": self.config.get("description", "No description provided"),
        }
