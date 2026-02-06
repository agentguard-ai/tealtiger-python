"""
TealTiger Guarded Clients

Drop-in replacements for AI provider clients with integrated security and cost tracking.
"""

from .teal_openai import (
    TealOpenAI,
    TealOpenAIConfig,
    ChatCompletionMessage,
    ChatCompletionRequest,
    SecurityMetadata,
    ChatCompletionResponse,
)

from .teal_anthropic import (
    TealAnthropic,
    TealAnthropicConfig,
    MessageCreateRequest,
    MessageCreateResponse,
)

from .teal_azure_openai import (
    TealAzureOpenAI,
    TealAzureOpenAIConfig,
    AzureChatCompletionMessage,
    AzureChatCompletionRequest,
    AzureChatCompletionResponse,
)

__all__ = [
    'TealOpenAI',
    'TealOpenAIConfig',
    'ChatCompletionMessage',
    'ChatCompletionRequest',
    'SecurityMetadata',
    'ChatCompletionResponse',
    'TealAnthropic',
    'TealAnthropicConfig',
    'MessageCreateRequest',
    'MessageCreateResponse',
    'TealAzureOpenAI',
    'TealAzureOpenAIConfig',
    'AzureChatCompletionMessage',
    'AzureChatCompletionRequest',
    'AzureChatCompletionResponse',
]
