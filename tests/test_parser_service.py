"""Tests for Conventional Commits Parser Service."""

import pytest
from mcp_server.services.parser_service import parse_commit, ParsedCommit


class TestParseCommit:
    """Test parse_commit function."""

    def test_simple_feat(self):
        """feat: add feature — без scope."""
        result = parse_commit("feat: add new feature")
        assert result is not None
        assert result.type == "feat"
        assert result.scope is None
        assert result.breaking is False
        assert result.description == "add new feature"

    def test_with_scope(self):
        """feat(api): add feature — с scope."""
        result = parse_commit("feat(api): add authentication endpoint")
        assert result is not None
        assert result.type == "feat"
        assert result.scope == "api"
        assert result.breaking is False
        assert result.description == "add authentication endpoint"

    def test_breaking_bang(self):
        """feat!: breaking change через ! в заголовке."""
        result = parse_commit("feat!: remove deprecated API")
        assert result is not None
        assert result.type == "feat"
        assert result.scope is None
        assert result.breaking is True
        assert result.description == "remove deprecated API"

    def test_breaking_in_body(self):
        """BREAKING CHANGE в теле коммита."""
        message = """feat(api): update authentication

BREAKING CHANGE: authentication method has changed"""
        result = parse_commit(message)
        assert result is not None
        assert result.type == "feat"
        assert result.scope == "api"
        assert result.breaking is True
        assert result.description == "update authentication"
        assert "authentication method has changed" in result.body

    def test_wip_returns_none(self):
        """WIP коммиты возвращают None."""
        wip_messages = [
            "WIP: working on feature",
            "wip: draft implementation",
            "Draft: do not review yet",
            "DO NOT MERGE: needs review",
        ]
        for message in wip_messages:
            result = parse_commit(message)
            assert result is None, f"Expected None for WIP message: {message}"

    def test_invalid_returns_none(self):
        """
        Невалидные форматы парсятся как 'non-conventional'.
        Только пустая строка и WIP возвращают None.
        """
        # Только пустая строка возвращает None
        assert parse_commit("") is None
        
        # Остальные "невалидные" форматы → non-conventional
        non_conventional_messages = [
            "invalid message",  # нет типа
            "feature: add something",  # неправильный тип (должно быть feat)
            "feat add something",  # нет двоеточия
            "feat(): empty scope",  # пустой scope
            "feat( ): space in scope",  # пробел в scope
            "123: numeric type",  # числовой тип
        ]
        for message in non_conventional_messages:
            result = parse_commit(message)
            assert result is not None, f"Expected ParsedCommit for: {message}"
            assert result.type == "non-conventional"

    def test_all_types(self):
        """Все поддерживаемые типы коммитов."""
        commit_types = [
            "feat", "fix", "perf", "refactor", "docs",
            "test", "style", "chore", "build", "ci", "revert"
        ]
        for commit_type in commit_types:
            message = f"{commit_type}: test description"
            result = parse_commit(message)
            assert result is not None, f"Type {commit_type} should be valid"
            assert result.type == commit_type
            assert result.description == "test description"

    def test_scope_with_hyphen(self):
        """Scope с дефисом (например, user-service)."""
        result = parse_commit("fix(user-service): resolve connection issue")
        assert result is not None
        assert result.type == "fix"
        assert result.scope == "user-service"
        assert result.breaking is False
        assert result.description == "resolve connection issue"

    def test_wip_in_description_not_wip(self):
        """WIP в описании — не WIP коммит (edge case после исправления)."""
        result = parse_commit("feat: add WIP tracking feature")
        assert result is not None
        assert result.type == "feat"
        assert result.description == "add WIP tracking feature"
        assert result.breaking is False

    def test_non_conventional_commit(self):
        """Не-Conventional Commits тоже парсятся (type='non-conventional')."""
        result = parse_commit("fixed stuff")
        assert result is not None
        assert result.type == "non-conventional"
        assert result.description == "fixed stuff"
        assert result.scope is None
        assert result.breaking is False

    def test_non_conventional_with_body(self):
        """Не-Conventional Commits с телом."""
        message = "update code\n\nThis commit updates the code."
        result = parse_commit(message)
        assert result is not None
        assert result.type == "non-conventional"
        assert result.description == "update code"
        assert result.body == "This commit updates the code."
