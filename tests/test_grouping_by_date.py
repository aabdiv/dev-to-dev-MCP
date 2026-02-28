"""Test grouping commits by date (not hash)."""

import pytest
from datetime import datetime

from mcp_server.services.analyzer import analyze_repo
from mcp_server.services.template_service import TemplateService


class TestGroupingByDate:
    """Test commit grouping by tag dates."""

    def test_grouping_by_date(self):
        """Группировка коммитов по датам тегов."""
        # Анализируем demo_project
        result = analyze_repo('demo_project')
        commits = result['commits']
        tags = result['tags']
        
        print(f"\n✅ Analyzed demo_project:")
        print(f"   Commits: {len(commits)}")
        print(f"   Tags: {len(tags)}")
        for tag in tags:
            print(f"   - {tag['name']}: {tag['date']}")
        
        # Создаём TemplateService
        ts = TemplateService()
        
        # Группируем коммиты по версиям
        versions = ts.group_commits_by_version(commits, tags)
        print(f"\n✅ Grouped into {len(versions)} versions:")
        for v in versions:
            print(f"   - {v.version}: {len(v.commits)} commits")
        
        # Проверяем что группировка правильная
        assert len(versions) == 3, f"Expected 3 versions, got {len(versions)}"
        
        version_names = [v.version for v in versions]
        assert version_names == ['v1.2.0', 'v1.1.0', 'v1.0.0'], \
            f"Expected ['v1.2.0', 'v1.1.0', 'v1.0.0'], got {version_names}"
        
        # Проверяем количество коммитов в каждой версии
        v1_0_0 = next(v for v in versions if v.version == 'v1.0.0')
        v1_1_0 = next(v for v in versions if v.version == 'v1.1.0')
        v1_2_0 = next(v for v in versions if v.version == 'v1.2.0')
        
        assert len(v1_0_0.commits) == 4, f"v1.0.0 should have 4 commits, got {len(v1_0_0.commits)}"
        assert len(v1_1_0.commits) == 6, f"v1.1.0 should have 6 commits, got {len(v1_1_0.commits)}"
        assert len(v1_2_0.commits) == 7, f"v1.2.0 should have 7 commits, got {len(v1_2_0.commits)}"
        
        print("\n✅ All assertions passed!")
        print("✅ Grouping by date works correctly!")

    def test_no_hash_based_grouping(self):
        """Проверка что группировка НЕ использует hash (только даты)."""
        # Это тест на будущее - если кто-то добавит группировку по hash
        # он должен быть явно указан в документации
        # Сейчас проверяем что используется только сравнение дат
        ts = TemplateService()
        
        # Создаём mock коммиты с одинаковым hash но разными датами
        date1 = datetime(2020, 1, 1, 10, 0, 0)
        date2 = datetime(2020, 1, 1, 12, 0, 0)
        date3 = datetime(2020, 1, 1, 15, 0, 0)
        
        mock_commits = []
        for date in [date1, date2, date3]:
            mock_commits.append(type('EnrichedCommit', (), {
                'hash': 'same_hash_123',  # Одинаковый hash
                'short_hash': 'same123',
                'date': date,
                'author': 'Test',
                'email': 'test@example.com',
                'parsed': type('ParsedCommit', (), {
                    'type': 'feat',
                    'scope': None,
                    'description': 'test commit',
                    'breaking': False
                })(),
                'files_changed': 1,
                'insertions': 10,
                'deletions': 0
            })())
        
        # Тег посередине
        mock_tags = [{
            'name': 'v1.0.0',
            'date': datetime(2020, 1, 1, 13, 0, 0),
            'hash': 'tag_hash'
        }]
        
        versions = ts.group_commits_by_version(mock_commits, mock_tags)
        
        # Группировка должна быть по дате, а не по hash
        # v1.0.0: коммиты до 13:00 (date1, date2)
        # Unreleased: коммиты после 13:00 (date3)
        assert len(versions) == 2
        v1_0_0 = next(v for v in versions if v.version == 'v1.0.0')
        unreleased = next(v for v in versions if v.version == 'Unreleased')
        
        assert len(v1_0_0.commits) == 2, "v1.0.0 should have 2 commits (by date)"
        assert len(unreleased.commits) == 1, "Unreleased should have 1 commit (by date)"
        
        print("✅ Hash-independent grouping verified!")

    def test_tag_dates_correct(self):
        """Проверка что даты тегов корректно извлечены."""
        result = analyze_repo('demo_project')
        tags = result['tags']
        
        assert len(tags) == 3, f"Expected 3 tags, got {len(tags)}"
        
        tag_names = [t['name'] for t in tags]
        assert 'v1.0.0' in tag_names
        assert 'v1.1.0' in tag_names
        assert 'v1.2.0' in tag_names
        
        # Проверяем что даты - datetime объекты
        for tag in tags:
            assert isinstance(tag['date'], datetime), \
                f"Tag {tag['name']} date should be datetime, got {type(tag['date'])}"
        
        # Проверяем порядок дат (должны быть отсортированы)
        dates = [t['date'] for t in tags]
        assert dates == sorted(dates), "Tags should be sorted by date"
        
        print("✅ Tag dates are correct!")

    def test_commits_sorted_by_date(self):
        """Проверка что коммиты отсортированы по дате."""
        result = analyze_repo('demo_project')
        commits = result['commits']
        
        assert len(commits) > 0, "Expected commits in demo_project"
        
        # Коммиты должны быть отсортированы от новых к старым (git default)
        dates = [c.date for c in commits]
        assert dates == sorted(dates, reverse=True), \
            "Commits should be sorted newest first"
        
        print(f"✅ {len(commits)} commits sorted by date (newest first)!")

    def test_all_commits_accounted(self):
        """Проверка что все коммиты распределены по версиям."""
        result = analyze_repo('demo_project')
        commits = result['commits']
        tags = result['tags']
        
        ts = TemplateService()
        versions = ts.group_commits_by_version(commits, tags)
        
        total_in_versions = sum(len(v.commits) for v in versions)
        
        assert total_in_versions == len(commits), \
            f"All commits should be accounted: {total_in_versions} in versions vs {len(commits)} total"
        
        print(f"✅ All {len(commits)} commits are accounted for!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
