"""Type definitions for AgentGuard SDK."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """Context for tool execution."""

    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SecurityDecision(BaseModel):
    """Security decision from policy evaluation."""

    allowed: bool = Field(..., description="Whether the action is allowed")
    reason: str = Field(..., description="Reason for the decision")
    policy_id: Optional[str] = Field(None, description="ID of the policy that made the decision")
    transformed: bool = Field(False, description="Whether the request was transformed")
    original_request: Optional[Dict[str, Any]] = Field(
        None, description="Original request if transformed"
    )


class ExecutionResult(BaseModel):
    """Result of tool execution."""

    success: bool = Field(..., description="Whether execution was successful")
    data: Optional[Any] = Field(None, description="Execution result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    security_decision: SecurityDecision = Field(..., description="Security decision")
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "execution_time": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        },
        description="Execution metadata",
    )


class Policy(BaseModel):
    """Security policy definition."""

    id: str = Field(..., description="Policy identifier")
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules")
    enabled: bool = Field(True, description="Whether policy is enabled")


class PolicyTestResult(BaseModel):
    """Result of policy testing."""

    decision: str = Field(..., description="Policy decision (allow/deny/transform)")
    reason: str = Field(..., description="Reason for the decision")
    matched_rules: List[str] = Field(default_factory=list, description="Rules that matched")
    transformed_request: Optional[Dict[str, Any]] = Field(
        None, description="Transformed request if applicable"
    )
