# 2026-02-27 — Тестирование analyzer.py

**Статус:** ✅ 25/25 тестов прошли, покрытие 94%  
**Участники:** User (Team Lead), Тестировщик, Разработчик

---

## Обзор

**Файл:** `src/mcp_server/services/analyzer.py`  
**Функций:** 5 публичных  
**Интеграция:** parser_service.py

---

## Найденные проблемы

| # | Проблема | Приоритет | Статус |
|---|----------|-----------|--------|
| 1 | **Invalid ref не обрабатывается** | Высокий | ⚠️ Требуется фикс |
| 2 | **Path injection уязвимость** | Критический | ⚠️ Требуется фикс |
| 3 | `commit.stats` может быть `None` | Средний | ✅ Частично обработано |

---

## Тесты (25 штук)

| Класс | Тестов | Описание | Статус |
|-------|--------|----------|--------|
| `TestGetRepo` | 4 | Открытие репозитория | ✅ PASS |
| `TestGetCommitsBetween` | 5 | Получение коммитов | ✅ PASS |
| `TestGetTags` | 4 | Список тегов | ✅ PASS |
| `TestAggregateStats` | 4 | Агрегация статистики | ✅ PASS |
| `TestAnalyzeRepo` | 5 | Полный анализ | ✅ PASS |
| `TestEdgeCases` | 3 | Merge commits, unicode | ✅ PASS |

**Покрытие:** 94% (63/67 строк)

---

## Критическая проблема #1: Path Injection

### Проблема

```python
# Текущий код:
def get_repo(repo_path: str) -> Repo:
    try:
        return Repo(repo_path)
    except Exception as e:
        raise InvalidRepoError(f"Not a git repository: {repo_path}") from e

# Уязвимость:
get_repo("../../../etc/passwd")  # Может прочитать любой файл!
get_repo("/tmp/../../../etc")    # Path traversal!
```

### Решение

```python
import os

def get_repo(repo_path: str) -> Repo:
    """Open git repository with path validation."""
    # Normalize and resolve to absolute path
    repo_path = os.path.abspath(os.path.normpath(repo_path))
    
    # Check if path exists
    if not os.path.exists(repo_path):
        raise InvalidRepoError(f"Path does not exist: {repo_path}")
    
    # Check if it's a git repository
    if not os.path.exists(os.path.join(repo_path, '.git')):
        raise InvalidRepoError(f"Not a git repository: {repo_path}")
    
    # Try to open
    try:
        return Repo(repo_path)
    except Exception as e:
        raise InvalidRepoError(f"Cannot open repository: {repo_path}") from e
```

---

## Проблема #2: Invalid Ref не обрабатывается

### Проблема

```python
# Текущий код:
def get_commits_between(repo, from_ref, to_ref):
    rev_range = f"{from_ref}..{to_ref}"
    git_commits = list(repo.iter_commits(rev_range))  # ❌ GitCommandError если ref невалидный

# Пример:
get_commits_between(repo, "nonexistent-tag", "HEAD")
# → GitCommandError: ambiguous argument
```

### Решение

```python
from git import GitCommandError

def get_commits_between(repo, from_ref, to_ref):
    # Resolve refs
    if to_ref is None:
        to_ref = "HEAD"
    
    if from_ref is None:
        rev_range = to_ref
    else:
        rev_range = f"{from_ref}..{to_ref}"
    
    # Get commits with error handling
    try:
        git_commits = list(repo.iter_commits(rev_range))
    except GitCommandError as e:
        raise InvalidRepoError(f"Invalid ref: {rev_range}") from e
    
    # ... rest of code
```

---

## Исправления

### Файл: analyzer.py (исправления)

```python
# В начало файла:
import os
from git import GitCommandError

# Исправить get_repo():
def get_repo(repo_path: str) -> Repo:
    """Open git repository with path validation."""
    # Normalize path
    repo_path = os.path.abspath(os.path.normpath(repo_path))
    
    # Check existence
    if not os.path.exists(repo_path):
        raise InvalidRepoError(f"Path does not exist: {repo_path}")
    
    # Check it's a git repo
    if not os.path.exists(os.path.join(repo_path, '.git')):
        raise InvalidRepoError(f"Not a git repository: {repo_path}")
    
    try:
        return Repo(repo_path)
    except Exception as e:
        raise InvalidRepoError(f"Cannot open repository: {repo_path}") from e

# Исправить get_commits_between():
def get_commits_between(repo, from_ref, to_ref):
    # ...
    try:
        git_commits = list(repo.iter_commits(rev_range))
    except GitCommandError as e:
        raise InvalidRepoError(f"Invalid ref: {rev_range}") from e
    # ...
```

---

## Рекомендации

### 1. Исправить path injection (Критический)
- Нормализация пути через `os.path.abspath(os.path.normpath())`
- Проверка существования пути
- Проверка наличия `.git/` директории

### 2. Исправить invalid ref (Высокий)
- Обработка `GitCommandError`
- Понятное сообщение об ошибке

### 3. Добавить тесты на ошибки
```python
def test_get_repo_path_injection():
    """Path injection должен быть заблокирован."""
    with pytest.raises(InvalidRepoError):
        get_repo("../../../etc/passwd")

def test_get_commits_invalid_ref():
    """Invalid ref должен выбрасывать ошибку."""
    with pytest.raises(InvalidRepoError):
        get_commits_between(repo, "nonexistent", "HEAD")
```

---

## Итог

**analyzer.py работоспособен:**
- ✅ 25/25 тестов прошли
- ✅ Покрытие 94%
- ⚠️ 2 проблемы требуют исправления

**Следующий шаг:**
Исправить проблемы и закоммитить.
