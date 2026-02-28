"""Integration tests for demo_project.

Tests analyzer.py on real (demo) git repository with:
- 17 commits
- 3 tags (v1.0.0, v1.1.0, v1.2.0)
- 1 breaking change
- 2 non-conventional commits
"""

import pytest

from mcp_server.services.analyzer import (
    analyze_repo,
    get_commits_between,
    get_repo,
    get_tags,
)


class TestDemoProject:
    """Test analyzer on demo_project."""

    def test_analyze_demo_project(self):
        """Анализ всего demo_project."""
        result = analyze_repo("demo_project")

        assert result["summary"]["total_commits"] == 17
        assert result["summary"]["by_type"]["feat"] == 6
        assert result["summary"]["by_type"]["non-conventional"] == 2
        assert len(result["tags"]) == 3

    def test_breaking_changes_detected(self):
        """Breaking change должен быть найден."""
        result = analyze_repo("demo_project")

        # Ищем breaking changes в коммитах
        breaking_commits = [c for c in result["commits"] if c.parsed.breaking]
        assert len(breaking_commits) == 1
        assert breaking_commits[0].parsed.type == "feat"
        assert "remove deprecated v1 API" in breaking_commits[0].parsed.description

    def test_tags_sorted(self):
        """Теги должны быть отсортированы по дате."""
        result = analyze_repo("demo_project")

        tag_names = [t["name"] for t in result["tags"]]
        assert tag_names == ["v1.0.0", "v1.1.0", "v1.2.0"]

    def test_commits_between_tags(self):
        """Коммиты между тегами."""
        repo = get_repo("demo_project")
        commits = get_commits_between(repo, "v1.0.0", "v1.1.0")

        # Между v1.0.0 и v1.1.0 должно быть 6 коммитов
        assert len(commits) == 6

    def test_non_conventional_commits(self):
        """Non-conventional коммиты должны парситься."""
        result = analyze_repo("demo_project")

        non_conv = [
            c for c in result["commits"] if c.parsed.type == "non-conventional"
        ]
        assert len(non_conv) == 2
        # Commits are returned newest first, so:
        # non_conv[0] = "temporary workaround until proper fix" (newer)
        # non_conv[1] = "quick fix for production issue" (older)
        descriptions = [c.parsed.description for c in non_conv]
        assert "quick fix for production issue" in descriptions
        assert "temporary workaround until proper fix" in descriptions

    def test_all_commit_types_present(self):
        """Проверка наличия всех типов коммитов."""
        result = analyze_repo("demo_project")

        by_type = result["summary"]["by_type"]

        # Ожидаемые типы коммитов
        assert "feat" in by_type
        assert "fix" in by_type
        assert "docs" in by_type
        assert "refactor" in by_type
        assert "test" in by_type
        assert "chore" in by_type
        assert "ci" in by_type
        assert "non-conventional" in by_type

    def test_commit_stats(self):
        """Проверка статистики коммитов."""
        result = analyze_repo("demo_project")

        stats = result["stats"]
        # Stats should be populated after fix
        assert stats["files_changed"] >= 0
        assert stats["insertions"] >= 0
        assert stats["deletions"] >= 0
        # At least some changes should exist
        total_changes = stats["insertions"] + stats["deletions"]
        assert total_changes > 0

    def test_author_stats(self):
        """Проверка статистики по авторам."""
        result = analyze_repo("demo_project")

        by_author = result["summary"]["by_author"]
        assert len(by_author) > 0
        # Все коммиты должны быть учтены
        total_by_author = sum(by_author.values())
        assert total_by_author == 17

    def test_commits_have_enriched_data(self):
        """Проверка обогащённых данных коммитов."""
        result = analyze_repo("demo_project")

        for commit in result["commits"]:
            assert commit.hash is not None
            assert len(commit.short_hash) == 7
            assert commit.author is not None
            assert commit.email is not None
            assert commit.date is not None
            assert isinstance(commit.files_changed, int)
            assert isinstance(commit.insertions, int)
            assert isinstance(commit.deletions, int)

    def test_tags_have_required_fields(self):
        """Проверка полей тегов."""
        result = analyze_repo("demo_project")

        for tag in result["tags"]:
            assert "name" in tag
            assert "hash" in tag
            assert "date" in tag
            assert tag["name"].startswith("v")

    def test_commits_order_chronological(self):
        """Коммиты должны быть в хронологическом порядке (новые первыми)."""
        result = analyze_repo("demo_project")

        commits = result["commits"]
        for i in range(len(commits) - 1):
            # Git iter_commits возвращает от новых к старым
            assert commits[i].date >= commits[i + 1].date

    def test_specific_commit_types_count(self):
        """Проверка точного количества коммитов по типам."""
        result = analyze_repo("demo_project")

        by_type = result["summary"]["by_type"]

        # Основано на логе demo_project
        assert by_type["feat"] == 6
        assert by_type["fix"] == 3
        assert by_type["docs"] == 2
        assert by_type["refactor"] == 1
        assert by_type["test"] == 1
        assert by_type["chore"] == 1
        assert by_type["ci"] == 1
        assert by_type["non-conventional"] == 2

    def test_commits_between_v1_1_0_and_v1_2_0(self):
        """Коммиты между v1.1.0 и v1.2.0."""
        repo = get_repo("demo_project")
        commits = get_commits_between(repo, "v1.1.0", "v1.2.0")

        # Проверка что коммиты есть
        assert len(commits) > 0

    def test_all_commits_to_head(self):
        """Все коммиты до HEAD."""
        repo = get_repo("demo_project")
        commits = get_commits_between(repo, None, "HEAD")

        assert len(commits) == 17

    def test_repo_path_normalization(self):
        """Проверка нормализации пути к репозиторию."""
        # Путь с ./ должен работать
        result = analyze_repo("./demo_project")
        assert result["summary"]["total_commits"] == 17

    def test_breaking_change_commit_details(self):
        """Детали breaking change коммита."""
        result = analyze_repo("demo_project")

        breaking_commits = [c for c in result["commits"] if c.parsed.breaking]
        assert len(breaking_commits) == 1

        commit = breaking_commits[0]
        assert commit.parsed.type == "feat"
        assert commit.parsed.scope == "api"  # feat(api)! имеет scope
        assert "remove deprecated v1 API" in commit.parsed.description
        assert commit.parsed.breaking is True

    def test_non_conventional_commit_details(self):
        """Детали non-conventional коммитов."""
        result = analyze_repo("demo_project")

        non_conv = [
            c for c in result["commits"] if c.parsed.type == "non-conventional"
        ]
        assert len(non_conv) == 2

        # Первый non-conventional коммит
        assert non_conv[0].parsed.type == "non-conventional"
        assert non_conv[0].parsed.scope is None
        assert non_conv[0].parsed.breaking is False

        # Второй non-conventional коммит
        assert non_conv[1].parsed.type == "non-conventional"
        assert non_conv[1].parsed.scope is None
        assert non_conv[1].parsed.breaking is False
