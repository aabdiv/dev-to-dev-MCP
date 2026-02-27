# 2026-02-27 — Тестирование parser_service.py

**Статус:** ✅ 8/8 тестов прошли, покрытие 100%  
**Участники:** User (Team Lead), Тестировщик

---

## Обзор

**Файл:** `src/mcp_server/services/parser_service.py`  
**Функция:** `parse_commit(message: str) -> ParsedCommit | None`

**Назначение:** Парсинг Conventional Commits с извлечением типа, scope, breaking changes.

---

## Найденные проблемы

| Приоритет | Проблема | Влияние |
|-----------|----------|---------|
| 🔴 Критический | Path injection в `_is_wip` | Ложные срабатывания на "WIP" в описании |
| 🟡 Средний | Нет валидации пустого description | `feat():` пройдёт |
| 🟢 Низкий | Нет нормализации ввода | Пробелы в начале/конце |

---

## Тесты (8 штук)

| № | Тест | Описание | Статус |
|---|------|----------|--------|
| 1 | `test_simple_feat` | `feat: description` без scope | ✅ PASS |
| 2 | `test_with_scope` | `feat(api): description` | ✅ PASS |
| 3 | `test_breaking_bang` | `feat!: description` | ✅ PASS |
| 4 | `test_breaking_in_body` | BREAKING CHANGE в теле | ✅ PASS |
| 5 | `test_wip_returns_none` | WIP/Draft → None | ✅ PASS |
| 6 | `test_invalid_returns_none` | 7 невалидных форматов | ✅ PASS |
| 7 | `test_all_types` | 11 типов коммитов | ✅ PASS |
| 8 | `test_scope_with_hyphen` | Scope с дефисом | ✅ PASS |

**Покрытие:** 100% (27/27 строк)

---

## Критическая проблема: _is_wip

### Проблема

```python
# Текущий код:
def _is_wip(message: str) -> bool:
    return any(pattern in message for pattern in WIP_PATTERNS)

# Ложное срабатывание:
parse_commit("feat: add WIP tracking")  # → None ❌
```

### Решение

```python
def _is_wip(message: str) -> bool:
    header = message.split('\n')[0].strip()
    return any(
        header.startswith(pattern) or header.lower().startswith(pattern.lower())
        for pattern in ["WIP:", "wip:", "Draft:", "DO NOT MERGE"]
    )
```

### Тест на edge case

```python
def test_wip_in_description_not_wip(self):
    """WIP в описании — не WIP коммит."""
    result = parse_commit("feat: add WIP tracking feature")
    assert result is not None
    assert result.type == "feat"
```

---

## Результаты pytest

```
============================== 8 passed in 0.03s ===============================

Name                                        Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------
src/mcp_server/services/parser_service.py      27      0   100%
```

---

## Рекомендации

### 1. Исправить `_is_wip` (Критический)
- Проверять только начало заголовка
- Не искать "WIP" во всём сообщении

### 2. Добавить валидацию description
- Проверять что description не пустой
- `feat():` должен вернуть None

### 3. Добавить нормализацию
- `.strip()` для message до обработки

---

## Следующий шаг

**Исправить `_is_wip` в parser_service.py**

После исправления:
- Добавить тест `test_wip_in_description_not_wip`
- Продолжить Итерацию 2 (analyzer.py)
