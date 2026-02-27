# 2026-02-27 — План Итерации 2: analyze_commits

**Статус:** ✅ План утверждён  
**Участники:** User (Team Lead), Разработчик

---

## Обзор Итерации 2

**Цель:** Реализовать полноценный tool `analyze_commits` с анализом Conventional Commits

**Компоненты:**
1. `parser.py` — Conventional Commits парсер
2. `analyzer.py` — GitPython анализатор
3. `analyze_commits` tool — MCP инструмент
4. `demo_project` — тестовый репозиторий

**Время:** 4-6 часов

---

## 1. Git Parser (`parser.py`)

### Назначение
Парсинг сообщений коммитов в формате Conventional Commits с извлечением структурированных данных.

### Структура модуля

```
parser.py
├── CONSTANTS
│   ├── COMMIT_TYPES: set[str]          # допустимые типы
│   ├── EMOJI_MAP: dict[str, str]       # emoji → type
│   └── WIP_PATTERNS: list[str]         # игнорируемые паттерны
│
├── REGEX_PATTERNS
│   ├── MAIN_PATTERN: re.Pattern        # основной regex
│   └── BREAKING_PATTERN: re.Pattern    # BREAKING CHANGE в теле
│
├── DATA CLASSES
│   └── ParsedCommit: dataclass
│
└── FUNCTIONS
    ├── parse_commit(message: str) -> ParsedCommit | None
    ├── _normalize_emoji(text: str) -> tuple[str, str | None]
    ├── _is_wip(message: str) -> bool
    └── _extract_breaking_change(body: str) -> bool
```

### Поддерживаемые типы

`feat, fix, perf, refactor, docs, test, style, chore, build, ci, revert`

### Emoji маппинг

| Emoji | Текстовый | Тип |
|-------|-----------|-----|
| ✨ | `:sparkles:` | feat |
| 🐛 | `:bug:` | fix |
| 📝 | `:memo:` | docs |
| ♻️ | `:recycle:` | refactor |

### Regex паттерны

```python
# Основной паттерн
^(?P<emoji>[:\w]+|[\U0001F300-\U0001F9FF]+)?\s*(?P<type>feat|fix|...)(\((?P<scope>[\w\-]+)\))?(?P<breaking>!)?:\s*(?P<description>.+)$

# BREAKING CHANGE в теле
^(?:BREAKING\s+CHANGE|BREAKING):\s*(?P<description>.+)$
```

### Логика работы `parse_commit`

1. Проверка на WIP → возврат `None`
2. Нормализация emoji
3. Применение основного regex
4. Если не совпало → упрощённый парсинг
5. Извлечение тела коммита
6. Поиск `BREAKING CHANGE` в теле
7. Возврат `ParsedCommit` или `None`

---

## 2. Git Analyzer (`analyzer.py`)

### Назначение
Анализ git-репозитория с использованием GitPython для извлечения коммитов, тегов и статистики.

### Структура модуля

```
analyzer.py
├── DATA CLASSES
│   ├── TagInfo: dataclass
│   ├── CommitInfo: dataclass
│   ├── AuthorStats: dataclass
│   └── VersionInfo: dataclass
│
├── EXCEPTIONS
│   ├── GitError: Exception
│   ├── InvalidRepoError: GitError
│   ├── InvalidRefError: GitError
│   └── RepoNotFoundError: GitError
│
└── FUNCTIONS
    ├── get_repo(repo_path: str) -> Repo
    ├── get_tags(repo: Repo) -> list[TagInfo]
    ├── get_commits_between(repo, from_ref, to_ref) -> list[CommitInfo]
    ├── get_commit_file_stats(repo, commit) -> dict
    ├── aggregate_by_author(commits) -> list[AuthorStats]
    ├── aggregate_by_type(commits) -> dict[str, int]
    ├── aggregate_by_scope(commits) -> list[str]
    ├── extract_breaking_changes(commits) -> list[dict]
    └── group_by_version(repo, parsed_commits) -> list[VersionInfo]
```

### Детали функций

**`get_repo(repo_path: str) -> Repo`**
- Проверка существования пути
- Валидация `.git/` директории
- Инициализация `git.Repo`

**`get_tags(repo: Repo) -> list[TagInfo]`**
- Фильтрация только аннотированных тегов
- Сортировка по дате
- Возврат: name, commit_hash, date

**`get_commits_between(repo, from_ref, to_ref)`**
- Валидация refs через `repo.commit(ref)`
- Использование `repo.iter_commits(f"{from_ref}..{to_ref}")`

**`group_by_version(repo, parsed_commits)`**
- Получение тегов сортированных по дате
- Для каждого тега: коммиты между предыдущим и текущим
- Unreleased: от последнего тега до HEAD

---

## 3. MCP Tool `analyze_commits`

### Сигнатура

```python
@mcp.tool()
async def analyze_commits(
    repo_path: Annotated[str, Field(description="Absolute path to git repo")],
    from_ref: Annotated[str | None, Field(description="Start ref. Default: latest tag")] = None,
    to_ref: Annotated[str | None, Field(description="End ref. Default: HEAD")] = None,
    commit_types: Annotated[list[str] | None, Field(description="Filter by types")] = None,
    max_commits: Annotated[int, Field(description="Max commits", ge=1, le=1000)] = 100,
    include_stats: Annotated[bool, Field(description="Include stats")] = True
) -> dict:
```

### Логика работы

```
1. VALIDATION
   • repo_path exists?
   • repo_path is git repo?
   • from_ref valid?
   • to_ref valid?
   
2. RESOLVE REFERENCES
   • from_ref = None → latest tag
   • to_ref = None → HEAD
   • No tags? → first commit
   
3. EXTRACT COMMITS
   • analyzer.get_commits_between()
   • Apply max_commits limit
   
4. PARSE COMMITS
   • parser.parse_commit() for each
   • Filter by commit_types
   • Skip WIP / unparseable
   
5. AGGREGATE
   • by_type: Counter
   • by_scope: unique list
   • by_author: name, email, count
   • breaking_changes: list
   • by_version: group_by_version()
   
6. RETURN STRUCTURED RESPONSE
```

### Структура возврата

```python
{
    # Meta
    "success": True,
    "repo_path": "/absolute/path",
    "from_ref": "v1.0.0",
    "to_ref": "HEAD",
    
    # Summary
    "total_commits": 42,
    "parsed_commits": 38,
    "skipped_commits": 4,
    
    # Aggregations
    "by_type": {"feat": 15, "fix": 20, ...},
    "by_scope": ["api", "ui", "core", ...],
    "authors": [{"name": "...", "email": "...", "commits": N}, ...],
    
    # Breaking changes
    "breaking_changes": [{"commit_hash": "...", "type": "feat", ...}],
    
    # Versions
    "versions": [{"tag": "v1.2.0", "date": "...", "commits": 12, ...}],
    
    # Unreleased
    "unreleased": {"commits": 5, "by_type": {...}, ...}
}
```

### Обработка ошибок

| Сценарий | Возврат |
|----------|---------|
| repo_path не существует | `{"success": False, "error": "Repository not found"}` |
| Не git репозиторий | `{"success": False, "error": "Not a git repository"}` |
| Invalid from_ref | `{"success": False, "error": "Invalid reference: {ref}"}` |
| Нет коммитов | `{"success": True, "total_commits": 0, ...}` |

---

## 4. Demo Project

### Назначение
Тестовый git-репозиторий для демонстрации и тестирования.

### Структура

```
demo_project/
├── .git/
├── README.md
├── pyproject.toml
├── src/
│   └── app.py
└── tests/
    └── test_app.py
```

### История коммитов (15 штук)

| # | Message | Type | Scope | Breaking | Emoji |
|---|---------|------|-------|----------|-------|
| 1 | `feat: initial commit` | feat | — | No | — |
| 2 | `feat(api): add user authentication` | feat | api | No | — |
| 3 | `fix(ui): resolve button alignment` | fix | ui | No | — |
| 4 | `docs: update README` | docs | — | No | — |
| **TAG v1.0.0** |
| 5 | `✨ add dark mode support` | feat | ui | No | ✨ |
| 6 | `feat!: remove deprecated v1 API` | feat | api | **Yes** | — |
| 7 | `fix(auth): handle edge case in login` | fix | auth | No | — |
| 8 | `refactor(core): optimize database queries` | refactor | core | No | — |
| 9 | `test: add integration tests` | test | — | No | — |
| 10 | `chore: update dependencies` | chore | — | No | — |
| **TAG v1.1.0** |
| 11 | `feat(api): add rate limiting` | feat | api | No | — |
| 12 | `🐛 fix memory leak in cache` | fix | cache | No | 🐛 |
| 13 | `docs(api): add API documentation` | docs | api | No | — |
| 14 | `ci: add GitHub Actions workflow` | ci | — | No | — |
| 15 | `feat: add export to CSV feature` | feat | — | No | — |
| **TAG v1.2.0 (HEAD)** |

### Теги

| Tag | Commit | Date | Commits |
|-----|--------|------|---------|
| `v1.0.0` | `d4e5f6g` | 2026-02-15 | 4 |
| `v1.1.0` | `j0k1l2m` | 2026-02-20 | 6 |
| `v1.2.0` | `o5p6q7r` | 2026-02-25 | 5 |

### Ожидаемая статистика

```python
{
    "total_commits": 15,
    "by_type": {"feat": 6, "fix": 3, "docs": 2, "refactor": 1, "test": 1, "chore": 1, "ci": 1},
    "by_scope": ["api", "ui", "auth", "core", "cache"],
    "breaking_changes": 1,
    "versions": [
        {"tag": "v1.0.0", "commits": 4, "breaking": 0},
        {"tag": "v1.1.0", "commits": 6, "breaking": 1},
        {"tag": "v1.2.0", "commits": 5, "breaking": 0}
    ]
}
```

---

## Зависимости

**pyproject.toml:**
```toml
[project.dependencies]
gitpython = "^3.1.43"

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23"]
```

---

## Структура файлов

```
src/
├── parser.py           # Conventional Commits parser
├── analyzer.py         # Git repository analyzer
├── tools.py            # MCP tools
└── mcp_server.py       # MCP server entry point

demo_project/
├── init.sh             # script to create test history
├── README.md
├── src/app.py
└── tests/test_app.py

tests/
├── test_parser.py
├── test_analyzer.py
└── test_tools.py
```

---

## Критерии завершения

- [ ] `parser.py` — парсит все форматы, тесты ≥90% coverage
- [ ] `analyzer.py` — извлекает коммиты/теги/статистику, тесты ≥90%
- [ ] `analyze_commits` tool — работает через MCP Inspector
- [ ] `demo_project` — 15 коммитов, 3 тега
- [ ] ai-logs — задокументирован процесс

---

## Следующий шаг

**Запуск Разработчика для реализации:**
1. Создать `parser.py`
2. Создать `analyzer.py`
3. Реализовать `analyze_commits` tool
4. Создать `demo_project`

**Затем:** Запуск Тестировщика для валидации
