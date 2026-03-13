"""LLM client abstraction layer with provider factory."""

from typing import Optional

from task_4_llm.client.base_llm_client import BaseLLMClient, SYSTEM_PROMPT
from task_4_llm.client.anthropic_client import AnthropicClient
from task_4_llm.client.gemini_client import GeminiClient

__all__: list[str] = [
    "BaseLLMClient",
    "AnthropicClient",
    "GeminiClient",
    "SYSTEM_PROMPT",
    "create_client",
]


def create_client(
    provider: str = "anthropic",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseLLMClient:
    """Factory function to create an LLM client.

    Args:
        provider: Provider name — ``"anthropic"`` or ``"gemini"``.
        api_key: API key for the provider. If ``None``, the
            respective SDK reads from its default environment
            variable.
        model: Override the default model for the provider.

    Returns:
        An instance of the appropriate ``BaseLLMClient`` subclass.

    Raises:
        ValueError: If the provider name is not recognized.
    """
    providers: dict[str, type[BaseLLMClient]] = {
        "anthropic": AnthropicClient,
        "gemini": GeminiClient,
    }

    client_cls: Optional[type[BaseLLMClient]] = providers.get(provider)
    if client_cls is None:
        supported: str = ", ".join(sorted(providers.keys()))
        raise ValueError(
            f"Unknown provider '{provider}'. Supported: {supported}"
        )

    kwargs: dict = {}
    if api_key is not None:
        kwargs["api_key"] = api_key
    if model is not None:
        kwargs["model"] = model

    return client_cls(**kwargs)
