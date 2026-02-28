"""GitHub Models client for release notes generation."""

import os
from typing import List

from .base import AIClient, AIGenerationError, ReleaseNotesStyle


class GitHubClient(AIClient):
    """GitHub Models implementation of AIClient."""

    DEFAULT_ENDPOINT = "https://models.github.ai/inference"
    DEFAULT_MODEL = "gpt-4.1-mini"  # Free model on GitHub Models

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None
    ):
        """
        Initialize GitHub Models client.

        Args:
            api_key: GitHub token. If None, reads from GITHUB_TOKEN env.
            base_url: GitHub Models endpoint. Default: https://models.github.ai/inference
            model: Model to use. Default: o3-mini

        Raises:
            AIGenerationError: If token not provided
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise AIGenerationError(
                "OpenAI package not installed. Run: pip install openai"
            )

        self.api_key = api_key or os.getenv("GITHUB_TOKEN")
        if not self.api_key:
            raise AIGenerationError(
                "GITHUB_TOKEN not set. Provide api_key or set GITHUB_TOKEN env variable. "
                "Get token from: https://github.com/settings/tokens"
            )

        self.base_url = base_url or os.getenv("GITHUB_AI_ENDPOINT", self.DEFAULT_ENDPOINT)
        self.model = model or os.getenv("AI_MODEL", self.DEFAULT_MODEL)

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate_release_notes(
        self,
        commits: List[dict],
        version: str,
        style: ReleaseNotesStyle = ReleaseNotesStyle.MARKDOWN,
        language: str = "ru"
    ) -> str:
        """Generate release notes using GitHub Models."""
        prompt = self._build_prompt(commits, version, style, language)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise AIGenerationError(f"GitHub Models API error: {e}") from e

    def _build_prompt(
        self,
        commits: List[dict],
        version: str,
        style: ReleaseNotesStyle,
        language: str
    ) -> str:
        """Build prompt for AI generation."""
        commits_text = self._format_commits(commits)
        
        style_instructions = {
            ReleaseNotesStyle.BRIEF: "Кратко, только ключевые изменения (3-5 пунктов)",
            ReleaseNotesStyle.DETAILED: "Подробно, со всеми изменениями и контекстом",
            ReleaseNotesStyle.MARKDOWN: "Стандартный Markdown формат с секциями",
        }

        return f"""
Сгенерируй release notes для версии {version}.

## Коммиты:
{commits_text}

## Требования:
- Стиль: {style_instructions[style]}
- Язык: {language}
- Формат: Markdown

## Структура:
1. ✨ Highlights (топ-3 фичи)
2. 🚀 Новые возможности (с контекстом использования)
3. ⚠️ Breaking Changes (с migration guide если есть)
4. 🐛 Исправления багов
5. 📊 Статистика (коммиты, авторы, файлы)

## Тон:
- Профессиональный но дружелюбный
- Фокус на пользе для пользователя
- Включай примеры кода где уместно
"""

    def _format_commits(self, commits: List[dict]) -> str:
        """Format commits for prompt."""
        lines = []
        for commit in commits[:50]:  # Limit to 50 commits
            parsed = commit.get('parsed', {})
            breaking = " ⚠️ BREAKING" if commit.get('breaking') else ""
            lines.append(
                f"- [{parsed.get('type', 'other')}] "
                f"{parsed.get('scope', '')}: "
                f"{parsed.get('description', commit.get('message', ''))}{breaking}"
            )
        return "\n".join(lines)

    def _get_system_prompt(self) -> str:
        """Get system prompt for AI."""
        return """Ты — профессиональный технический писатель.
Твоя задача — создавать понятные release notes на основе коммитов.
Фокусируйся на пользе для пользователя, а не на технических деталях."""
