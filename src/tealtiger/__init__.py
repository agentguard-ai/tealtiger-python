"""TealTiger Python SDK - Enterprise-grade security for AI agents."""

from TealTiger.client import TealTiger
from TealTiger.policy import PolicyBuilder, PolicyTester
from TealTiger.types import ExecutionResult, SecurityDecision
from TealTiger.guardrails import (
    Guardrail,
    GuardrailResult,
    GuardrailEngine,
    GuardrailEngineResult,
    PIIDetectionGuardrail,
    ContentModerationGuardrail,
    PromptInjectionGuardrail,
)

# Cost tracking and budget management
from TealTiger.cost import (
    # Types
    ModelProvider,
    BudgetPeriod,
    BudgetAction,
    AlertSeverity,
    ModelPricing,
    TokenUsage,
    CostBreakdown,
    CostEstimate,
    CostRecord,
    BudgetScope,
    BudgetConfig,
    BudgetStatus,
    CostAlert,
    CostSummary,
    # Pricing
    MODEL_PRICING,
    get_model_pricing,
    get_provider_models,
    is_model_supported,
    get_supported_models,
    get_supported_providers,
    # Tracker
    CostTracker,
    CostTrackerConfig,
)

# Storage and budget management
from TealTiger.cost.storage import CostStorage, InMemoryCostStorage
from TealTiger.cost.budget import BudgetManager

# Guarded AI clients
from TealTiger.clients import (
    TealOpenAI,
    TealOpenAIConfig,
    TealAnthropic,
    TealAnthropicConfig,
    TealAzureOpenAI,
    TealAzureOpenAIConfig,
)

__version__ = "1.0.0"
__all__ = [
    # Core client
    "TealTiger",
    "PolicyBuilder",
    "PolicyTester",
    "ExecutionResult",
    "SecurityDecision",
    # Guardrails
    "Guardrail",
    "GuardrailResult",
    "GuardrailEngine",
    "GuardrailEngineResult",
    "PIIDetectionGuardrail",
    "ContentModerationGuardrail",
    "PromptInjectionGuardrail",
    # Cost tracking types
    "ModelProvider",
    "BudgetPeriod",
    "BudgetAction",
    "AlertSeverity",
    "ModelPricing",
    "TokenUsage",
    "CostBreakdown",
    "CostEstimate",
    "CostRecord",
    "BudgetScope",
    "BudgetConfig",
    "BudgetStatus",
    "CostAlert",
    "CostSummary",
    # Pricing functions
    "MODEL_PRICING",
    "get_model_pricing",
    "get_provider_models",
    "is_model_supported",
    "get_supported_models",
    "get_supported_providers",
    # Cost tracking
    "CostTracker",
    "CostTrackerConfig",
    "CostStorage",
    "InMemoryCostStorage",
    # Budget management
    "BudgetManager",
    # Guarded clients
    "TealOpenAI",
    "TealOpenAIConfig",
    "TealAnthropic",
    "TealAnthropicConfig",
    "TealAzureOpenAI",
    "TealAzureOpenAIConfig",
]

