"""AI Client abstraction for release notes generation."""

from enum import Enum
from typing import List, Protocol


class ReleaseNotesStyle(str, Enum):
    """Output style for release notes."""
    
    BRIEF = "brief"           # Кратко, только главное
    DETAILED = "detailed"     # Подробно со всеми деталями
    MARKDOWN = "markdown"     # Стандартный Markdown формат


class AIClient(Protocol):
    """Protocol for AI release notes generation clients."""

    def generate_release_notes(
        self,
        commits: List[dict],
        version: str,
        style: ReleaseNotesStyle = ReleaseNotesStyle.MARKDOWN,
        language: str = "ru"
    ) -> str:
        """
        Generate release notes using AI.

        Args:
            commits: List of enriched commit dicts
            version: Version string (e.g., 'v1.2.0')
            style: Output style
            language: Language code (default: Russian)

        Returns:
            Generated release notes as string

        Raises:
            AIGenerationError: If AI generation fails
        """
        ...


class AIGenerationError(Exception):
    """Raised when AI generation fails."""
    pass
