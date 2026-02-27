# SPEC.md — Git Changelog MCP Server

**Статус:** Утверждено | **Версия:** 2.0 | **Дата:** 27 февраля 2026 г.

---

## 1. Концепция

**git-changelog-mcp** — MCP-сервер для AI-агентов: анализ git-истории, генерация changelog и release notes по Conventional Commits. Локальная работа, Docker ≤500 МБ.

---

## 2. Архитектура

### 2.1 Компоненты

| Тип | Кол-во | Назначение | Пример |
|-----|--------|------------|--------|
| **Tools** | 3 | Действия с параметрами | `analyze_commits(repo, from, to)` |
| **Resources** | 3 | Read-only данные по URI | `git://tags/{repo}` |
| **Prompts** | 2 | Workflow-чеклисты | `draft-release` |

### 2.2 Диаграмма

```
AI Agent ──MCP──► FastMCP Server:8000
                    ├─ Tools (analyze, changelog, release)
                    ├─ Resources (tags, commits, stats)
                    └─ Prompts (draft, summarize)
                         │
                         ▼
                  Git Repository (.git)
```

---

## 3. Компоненты

### 3.1 Tools

**analyze_commits**
```python
async def analyze_commits(repo_path: str, from_ref: str|None=None, to_ref: str|None=None,
                          commit_types: list[str]|None=None, max_commits: int=100,
                          include_stats: bool=True) -> dict:
```
Анализ коммитов с категоризацией, статистикой, breaking changes. **Возврат:** `{commits, summary, stats, breaking_changes}`

**generate_changelog**
```python
async def generate_changelog(repo_path: str, from_ref: str|None=None, to_ref: str|None=None,
                             format: str="markdown", template: str|None=None,
                             group_by_type: bool=True, include_commit_links: bool=True) -> str:
```
Генерация CHANGELOG (markdown/json/plain). **Возврат:** Строка changelog

**generate_release_notes**
```python
async def generate_release_notes(repo_path: str, version: str, from_ref: str|None=None,
                                 to_ref: str|None=None, highlight_breaking: bool=True,
                                 include_migration_guide: bool=True) -> dict:
```
Release notes с breaking changes и migration guide. **Возврат:** `{title, content, breaking_changes, migration_guide, metadata}`

---

### 3.2 Resources

| URI | Функция | Возврат |
|-----|---------|---------|
| `git://tags/{repo}` | `list_tags(repo)` | `[{name, commit, date}, ...]` |
| `git://commits/{repo}/{from}/{to}` | `get_raw_commits(repo, from, to)` | `[{hash, message, author, date}, ...]` |
| `git://stats/{repo}/{from}/{to}` | `get_quick_stats(repo, from, to)` | `{total_commits, contributors, date_range}` |

---

### 3.3 Prompts

| Промпт | Описание |
|--------|----------|
| `draft-release` | Чеклист релиза: версия → теги → анализ → notes → breaking changes → публикация |
| `summarize-changes` | Резюме для менеджеров: бизнес-группировка, упрощение, топ-3 изменения |

---

## 4. План итераций

### Итерация 1: Скелет 
**Чек-лист:**
- [x] pyproject.toml (fastmcp, gitpython, jinja2, uvicorn)
- [x] Структура src/mcp_server/{tools,resources,prompts,services,models}
- [x] FastMCP сервер + /health endpoint
- [x] Dockerfile (Alpine 3.11)
- [x] demo_project/ с git-историей

**Готовность:** `docker build` ≤500 МБ, `curl :8000/health` → 200 OK

---

### Итерация 2: analyze_commits
**Чек-лист:**
- [ ] ParserService (Conventional Commits)
- [ ] Pydantic модели (Commit, Stats)
- [ ] `analyze_commits` с фильтрацией
- [ ] Статистика (files/+/−)
- [ ] Breaking changes detection
- [ ] Unit тесты

**Готовность:** Парсер работает, breaking changes, покрытие 80%+

**Время:** 3-4 часа

---

### Итерация 3: generate_changelog
**Чек-лист:**
- [ ] TemplateService (Jinja2)
- [ ] Шаблоны (default/compact/detailed)
- [ ] `generate_changelog` (md/json/plain)
- [ ] Группировка по типам
- [ ] Ссылки на коммиты
- [ ] Unit тесты

**Готовность:** Валидный Markdown, группировка, ссылки

**Время:** 3-4 часа

---

### Итерация 4: generate_release_notes
**Чек-лист:**
- [ ] `generate_release_notes`
- [ ] Breaking changes секция
- [ ] Migration guide
- [ ] Авто-определение предыдущего тега
- [ ] Unit тесты

**Готовность:** Notes со всеми секциями, migration guide

**Время:** 2-3 часа

---

### Итерация 5: Resources
**Чек-лист:**
- [ ] `git://tags/{repo}`
- [ ] `git://commits/{repo}/{from}/{to}`
- [ ] `git://stats/{repo}/{from}/{to}`
- [ ] URI валидация
- [ ] Unit тесты

**Готовность:** 3 Resources работают, формат возврата корректен

**Время:** 2-3 часа

---

### Итерация 6: Prompts + Полировка
**Чек-лист:**
- [ ] Prompt `draft-release`
- [ ] Prompt `summarize-changes`
- [ ] Multi-stage Docker
- [ ] Логирование (ai-logs/)
- [ ] Integration тесты

**Готовность:** Prompts направляют, Docker ≤500 МБ

**Время:** 1-2 часа

---

### Итерация 7: Демо
**Чек-лист:**
- [ ] `scripts/smoke_test.sh`
- [ ] End-to-end тесты
- [ ] Демо-сценарий (7 мин)
- [ ] Документация

**Готовность:** Smoke test проходит, все компоненты работают

**Время:** 2 часа

---

## 5. Приоритеты

| Компонент | Приоритет | Время |
|-----------|-----------|-------|
| analyze_commits | MUST | 3-4ч |
| generate_changelog | MUST | 3-4ч |
| generate_release_notes | SHOULD | 2-3ч |
| git://tags | SHOULD | 1ч |
| git://commits | SHOULD | 1ч |
| git://stats | NICE | 0.5ч |
| draft-release | NICE | 0.5ч |
| summarize-changes | NICE | 0.5ч |

**MVP:** analyze + changelog + Docker + /health

---

## 6. Критерии успеха

**Обязательные:**
- [ ] 3 Tools работают
- [ ] 3 Resources читаются
- [ ] 2 Prompts направляют
- [ ] Локально, без внешних API
- [ ] Docker ≤500 МБ
- [ ] Покрытие тестов >80%

**Метрики:** Запуск <5 сек | Ответ <1 сек | Линтеры: 0 ошибок

---

## 7. Технический стек

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.11+ |
| MCP | FastMCP 3.0+ |
| Git | GitPython 3.1.40+ |
| Templates | Jinja2 3.1+ |
| Server | Uvicorn 0.27+ |
| Testing | pytest 8.0+ |
| Linting | ruff 0.2+ |

**Структура:**
```
src/mcp_server/
├── server.py
├── tools/{analyze,changelog,release}.py
├── resources/{tags,commits,stats}.py
├── prompts/{draft,summarize}.py
├── services/{git,parser,template}.py
└── models/{commit,changelog,release}.py
```

---

**Объём:** ~220 строк
