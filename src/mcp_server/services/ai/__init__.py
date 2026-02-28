"""AI services for release notes generation."""

import os
from typing import Optional

from .base import AIClient, AIGenerationError, ReleaseNotesStyle


def get_ai_client(
    provider: str | None = None,
    api_key: Optional[str] = None,
    **kwargs
) -> AIClient:
    """
    Get AI client for specified provider.

    Args:
        provider: AI provider (github, openai, ollama). Auto-detected from env if None.
        api_key: API key (optional, can be from env)
        **kwargs: Provider-specific arguments

    Returns:
        AIClient instance

    Raises:
        AIGenerationError: If provider not supported or not configured
    """
    # Auto-detect provider from env or use default
    if provider is None:
        provider = os.getenv("AI_PROVIDER", "github")
    
    if provider == "github":
        from .github_client import GitHubClient
        return GitHubClient(api_key=api_key, **kwargs)
    
    elif provider == "openai":
        # For future OpenAI support
        raise AIGenerationError(
            "OpenAI provider not yet implemented. Use 'github' provider for now."
        )
    
    elif provider == "ollama":
        # For future Ollama support
        raise AIGenerationError(
            "Ollama provider not yet implemented. Use 'github' provider for now."
        )
    
    else:
        raise AIGenerationError(
            f"Unknown provider: {provider}. Supported: github"
        )


__all__ = ["AIClient", "AIGenerationError", "ReleaseNotesStyle", "get_ai_client"]
