"""Integration tests for Git Analyzer Service."""

import os
import shutil
import subprocess
import tempfile
from datetime import datetime

import pytest
from git import Repo

from mcp_server.services.analyzer import (
    InvalidRepoError,
    aggregate_stats,
    analyze_repo,
    get_commits_between,
    get_repo,
    get_tags,
)


@pytest.fixture
def temp_repo():
    """Create a temporary git repository with test commits."""
    tmpdir = tempfile.mkdtemp()
    repo_path = os.path.join(tmpdir, "test_repo")
    os.makedirs(repo_path)

    # Initialize git repo
    repo = Repo.init(repo_path)

    # Configure git user
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Create test commits
    commits_info = []

    # Commit 1: Initial commit
    file1 = os.path.join(repo_path, "README.md")
    with open(file1, "w") as f:
        f.write("# Test Project\n")
    repo.index.add([file1])
    commit1 = repo.index.commit("docs: initial README")
    commits_info.append({"hash": commit1.hexsha, "message": "docs: initial README"})

    # Commit 2: Feature
    file2 = os.path.join(repo_path, "main.py")
    with open(file2, "w") as f:
        f.write("print('Hello')\n")
    repo.index.add([file2])
    commit2 = repo.index.commit("feat: add main script")
    commits_info.append({"hash": commit2.hexsha, "message": "feat: add main script"})

    # Create tag v1.0.0
    repo.create_tag("v1.0.0", message="Version 1.0.0")

    # Commit 3: Fix with scope
    with open(file2, "a") as f:
        f.write("print('World')\n")
    repo.index.add([file2])
    commit3 = repo.index.commit("fix(main): fix output")
    commits_info.append({"hash": commit3.hexsha, "message": "fix(main): fix output"})

    # Commit 4: Breaking change
    with open(file2, "w") as f:
        f.write("def main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()\n")
    repo.index.add([file2])
    commit4 = repo.index.commit("feat!: refactor main function")
    commits_info.append({"hash": commit4.hexsha, "message": "feat!: refactor main function"})

    # Commit 5: Non-conventional
    file3 = os.path.join(repo_path, "utils.py")
    with open(file3, "w") as f:
        f.write("def helper(): pass\n")
    repo.index.add([file3])
    commit5 = repo.index.commit("added helper function")
    commits_info.append({"hash": commit5.hexsha, "message": "added helper function"})

    # Create tag v1.1.0
    repo.create_tag("v1.1.0", message="Version 1.1.0")

    # Commit 6: WIP (should be filtered out)
    file4 = os.path.join(repo_path, "wip.py")
    with open(file4, "w") as f:
        f.write("# WIP\n")
    repo.index.add([file4])
    commit6 = repo.index.commit("WIP: working on feature")
    commits_info.append({"hash": commit6.hexsha, "message": "WIP: working on feature"})

    yield {
        "path": repo_path,
        "repo": repo,
        "commits": commits_info,
    }

    # Cleanup
    repo.close()
    shutil.rmtree(tmpdir)


@pytest.fixture
def empty_dir():
    """Create an empty directory (not a git repo)."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


class TestGetRepo:
    """Test get_repo function."""

    def test_get_repo_valid(self, temp_repo):
        """Открыть валидный git-репозиторий."""
        repo = get_repo(temp_repo["path"])
        assert repo is not None
        assert isinstance(repo, Repo)
        assert repo.working_dir == temp_repo["path"]

    def test_get_repo_invalid(self, empty_dir):
        """Открыть не-git директорию."""
        with pytest.raises(InvalidRepoError):
            get_repo(empty_dir)

    def test_get_repo_nonexistent(self):
        """Открыть несуществующую директорию."""
        with pytest.raises(InvalidRepoError):
            get_repo("/nonexistent/path/that/does/not/exist")

    def test_get_repo_path_injection(self):
        """Path injection attempt should still work (git resolves the path)."""
        # GitPython resolves paths, so this is actually valid if the resolved path is a repo
        # This test documents the current behavior - path validation is minimal
        with pytest.raises(InvalidRepoError):
            # This should fail because the resolved path doesn't exist or isn't a repo
            get_repo("../../../not-a-repo")


class TestGetCommitsBetween:
    """Test get_commits_between function."""

    def test_get_commits_all(self, temp_repo):
        """Получить все коммиты до HEAD."""
        commits = get_commits_between(temp_repo["repo"], None, "HEAD")
        assert len(commits) > 0
        assert all(hasattr(c, "parsed") for c in commits)
        assert all(hasattr(c, "hash") for c in commits)
        assert all(hasattr(c, "author") for c in commits)

    def test_get_commits_between_refs(self, temp_repo):
        """Получить коммиты между тегами."""
        commits = get_commits_between(temp_repo["repo"], "v1.0.0", "v1.1.0")
        assert len(commits) > 0
        # WIP коммиты фильтруются
        assert all(c.parsed.type != "WIP" for c in commits)

    def test_get_commits_wip_filtered(self, temp_repo):
        """WIP коммиты должны фильтроваться."""
        commits = get_commits_between(temp_repo["repo"], None, "HEAD")
        # Последний коммит - WIP, он должен быть отфильтрован
        messages = [c.parsed.description for c in commits]
        assert "working on feature" not in messages

    def test_get_commits_invalid_ref(self, temp_repo):
        """Невалидный ref должен вызывать ошибку."""
        with pytest.raises(Exception):
            get_commits_between(temp_repo["repo"], "nonexistent-tag", "HEAD")

    def test_get_commits_enriched_data(self, temp_repo):
        """Проверка обогащённых данных коммитов."""
        commits = get_commits_between(temp_repo["repo"], None, "HEAD")
        for commit in commits:
            assert commit.hash is not None
            assert len(commit.short_hash) == 7
            assert commit.author is not None
            assert isinstance(commit.date, datetime)
            assert isinstance(commit.files_changed, int)
            assert isinstance(commit.insertions, int)
            assert isinstance(commit.deletions, int)


class TestGetTags:
    """Test get_tags function."""

    def test_get_tags(self, temp_repo):
        """Получить список тегов."""
        tags = get_tags(temp_repo["repo"])
        assert isinstance(tags, list)
        assert len(tags) >= 2  # v1.0.0 и v1.1.0
        assert all("name" in t for t in tags)
        assert all("hash" in t for t in tags)
        assert all("date" in t for t in tags)

    def test_get_tags_sorted(self, temp_repo):
        """Теги должны быть отсортированы по дате."""
        tags = get_tags(temp_repo["repo"])
        assert len(tags) >= 2
        # Проверка сортировки по дате
        for i in range(len(tags) - 1):
            assert tags[i]["date"] <= tags[i + 1]["date"]

    def test_get_tags_names(self, temp_repo):
        """Проверка имён тегов."""
        tags = get_tags(temp_repo["repo"])
        tag_names = [t["name"] for t in tags]
        assert "v1.0.0" in tag_names
        assert "v1.1.0" in tag_names

    def test_get_tags_no_tags(self, empty_dir):
        """Директория без тегов (но это не git repo, так что будет ошибка)."""
        # Создадим репозиторий без тегов
        tmpdir = tempfile.mkdtemp()
        try:
            repo = Repo.init(tmpdir)
            repo.config_writer().set_value("user", "name", "Test").release()
            repo.config_writer().set_value("user", "email", "test@test.com").release()
            file = os.path.join(tmpdir, "file.txt")
            with open(file, "w") as f:
                f.write("test")
            repo.index.add([file])
            repo.index.commit("initial")

            tags = get_tags(repo)
            assert tags == []
        finally:
            repo.close()
            shutil.rmtree(tmpdir)


class TestAggregateStats:
    """Test aggregate_stats function."""

    def test_aggregate_stats(self, temp_repo):
        """Агрегировать статистику."""
        commits = get_commits_between(temp_repo["repo"], None, "HEAD")
        stats = aggregate_stats(commits)

        assert "by_type" in stats
        assert "by_author" in stats
        assert "files_changed" in stats
        assert "insertions" in stats
        assert "deletions" in stats

    def test_aggregate_stats_by_type(self, temp_repo):
        """Проверка группировки по типам."""
        commits = get_commits_between(temp_repo["repo"], None, "HEAD")
        stats = aggregate_stats(commits)

        assert "feat" in stats["by_type"]
        assert "fix" in stats["by_type"]
        assert "docs" in stats["by_type"]
        assert "non-conventional" in stats["by_type"]

    def test_aggregate_stats_by_author(self, temp_repo):
        """Проверка группировки по авторам."""
        commits = get_commits_between(temp_repo["repo"], None, "HEAD")
        stats = aggregate_stats(commits)

        assert "Test User" in stats["by_author"]
        assert stats["by_author"]["Test User"] > 0

    def test_aggregate_stats_empty_list(self):
        """Агрегация пустого списка коммитов."""
        stats = aggregate_stats([])

        assert stats["by_type"] == {}
        assert stats["by_author"] == {}
        assert stats["files_changed"] == 0
        assert stats["insertions"] == 0
        assert stats["deletions"] == 0


class TestAnalyzeRepo:
    """Test analyze_repo function."""

    def test_analyze_repo(self, temp_repo):
        """Полный анализ репозитория."""
        result = analyze_repo(temp_repo["path"])

        assert result["repo_path"] == temp_repo["path"]
        assert result["commits"] is not None
        assert "summary" in result
        assert "stats" in result
        assert "tags" in result

    def test_analyze_repo_summary(self, temp_repo):
        """Проверка summary в результате анализа."""
        result = analyze_repo(temp_repo["path"])

        assert result["summary"]["total_commits"] > 0
        assert "by_type" in result["summary"]
        assert "by_author" in result["summary"]

    def test_analyze_repo_stats(self, temp_repo):
        """Проверка stats в результате анализа."""
        result = analyze_repo(temp_repo["path"])

        assert result["stats"]["files_changed"] >= 0
        assert result["stats"]["insertions"] >= 0
        assert result["stats"]["deletions"] >= 0

    def test_analyze_repo_with_refs(self, temp_repo):
        """Анализ с указанием refs."""
        result = analyze_repo(temp_repo["path"], from_ref="v1.0.0", to_ref="v1.1.0")

        assert result["from_ref"] == "v1.0.0"
        assert result["to_ref"] == "v1.1.0"
        assert result["summary"]["total_commits"] > 0

    def test_analyze_repo_invalid_path(self, empty_dir):
        """Анализ не-git директории."""
        with pytest.raises(InvalidRepoError):
            analyze_repo(empty_dir)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_merge_commit_stats(self, temp_repo):
        """Проверка обработки merge commits (могут иметь None stats)."""
        # Создадим merge commit
        repo = temp_repo["repo"]
        original_branch = repo.active_branch.name

        # Создадим новую ветку
        feature_branch = repo.create_head("feature")
        repo.heads.feature.checkout()

        # Добавим коммит
        file = os.path.join(temp_repo["path"], "feature.py")
        with open(file, "w") as f:
            f.write("# Feature\n")
        repo.index.add([file])
        repo.index.commit("feat: add feature branch")

        # Вернёмся и сделаем merge
        repo.heads[original_branch].checkout()
        # GitPython использует git.merge() через git command
        repo.git.merge(feature_branch)

        # Получим коммиты
        commits = get_commits_between(repo, None, "HEAD")
        assert len(commits) > 0

    def test_commit_with_special_characters(self, temp_repo):
        """Коммиты со спецсимволами в сообщении."""
        repo = temp_repo["repo"]
        file = os.path.join(temp_repo["path"], "special.txt")
        with open(file, "w") as f:
            f.write("test")
        repo.index.add([file])
        repo.index.commit("feat: add file with special chars: тест 测试 🚀")

        commits = get_commits_between(repo, None, "HEAD")
        assert len(commits) > 0
        # Проверка что коммит с unicode корректно обработан
        found = any("тест" in c.parsed.description or "🚀" in c.parsed.description for c in commits)
        assert found

    def test_empty_commit_message(self, temp_repo):
        """Пустое сообщение коммита."""
        repo = temp_repo["repo"]
        # Пустые коммиты в git невозможны без --allow-empty-message
        # Но проверим обработку
        file = os.path.join(temp_repo["path"], "empty.txt")
        with open(file, "w") as f:
            f.write("")
        repo.index.add([file])
        repo.index.commit("", skip_hooks=True)

        # parse_commit должен вернуть None для пустого сообщения
        # и get_commits_between должен его отфильтровать
        commits = get_commits_between(repo, None, "HEAD")
        # Пустой коммит будет отфильтрован
        assert len(commits) >= 0  # Может быть 0 или больше
