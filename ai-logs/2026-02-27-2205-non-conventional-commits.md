# 2026-02-27 — Non-conventional коммиты в parser_service.py

**Статус:** ✅ 11/11 тестов прошли, покрытие 100%  
**Участники:** User (Team Lead), Разработчик, Тестировщик

---

## Изменение по запросу User

> Нужно сделать так, чтобы сообщение оформленное не по правилам Conventional Commits тоже рассматривалось.
> Пусть для него будет определен type 'non-conventional', но при этом мы сохраним хотя бы текст коммита.
> Не всегда разработчики правильно оформляют коммиты, но информацию о них сохранить и обработать все равно хотелось бы.

---

## Внесённые изменения

### 1. Добавлена константа

```python
NON_CONVENTIONAL_TYPE = "non-conventional"
```

### 2. Обновлена логика `parse_commit()`

**Было:**
```python
match = MAIN_PATTERN.match(header)
if not match:
    return None  # ❌ Невалидные коммиты игнорировались
```

**Стало:**
```python
match = MAIN_PATTERN.match(header)
if match:
    # Conventional commit
    return ParsedCommit(type=match.group('type'), ...)

# Non-conventional commit
return ParsedCommit(
    type=NON_CONVENTIONAL_TYPE,
    description=header,
    scope=None,
    breaking=False
)
```

### 3. Обработка пустой строки

```python
# Empty message
if not header:
    return None  # Пустые сообщения игнорируем
```

---

## Примеры работы

### Conventional Commits

```python
parse_commit("feat(api): add auth")
# → ParsedCommit(type='feat', scope='api', description='add auth')

parse_commit("feat!: remove API")
# → ParsedCommit(type='feat', breaking=True)
```

### Non-conventional Commits

```python
parse_commit("fixed stuff")
# → ParsedCommit(type='non-conventional', description='fixed stuff')

parse_commit("update code")
# → ParsedCommit(type='non-conventional', description='update code')

parse_commit("refactored the thing")
# → ParsedCommit(type='non-conventional', description='refactored the thing')
```

### WIP (игнорируются)

```python
parse_commit("WIP: working on it")
# → None

parse_commit("Draft: do not review")
# → None
```

### Пустые

```python
parse_commit("")
# → None
```

---

## Новые тесты

Добавлено 2 теста:

### test_non_conventional_commit
```python
def test_non_conventional_commit(self):
    """Не-Conventional Commits тоже парсятся (type='non-conventional')."""
    result = parse_commit("fixed stuff")
    assert result.type == "non-conventional"
    assert result.description == "fixed stuff"
```

### test_non_conventional_with_body
```python
def test_non_conventional_with_body(self):
    """Не-Conventional Commits с телом."""
    message = "update code\n\nThis commit updates the code."
    result = parse_commit(message)
    assert result.type == "non-conventional"
    assert result.body == "This commit updates the code."
```

---

## Обновлённый тест

### test_invalid_returns_none

**Было:**
```python
# Все "невалидные" форматы → None
assert parse_commit("invalid message") is None
```

**Стало:**
```python
# Только пустая строка → None
assert parse_commit("") is None

# Остальные "невалидные" → non-conventional
assert parse_commit("invalid message").type == "non-conventional"
```

---

## Результаты тестов

```
============================== 11 passed in 0.03s ===============================

Name                                        Stmt   Miss  Cover   Missing
-------------------------------------------------------------------------
src/mcp_server/services/parser_service.py      33      0   100%
```

✅ **Все 11 тестов прошли**  
✅ **Покрытие 100%**

---

## Преимущества изменения

| Преимущество | Описание |
|--------------|----------|
| **Полнота данных** | Все коммиты сохраняются, не только Conventional |
| **Гибкость** | Реальные проекты редко используют 100% Conventional Commits |
| **Статистика** | Можно показать сколько коммитов оформлены правильно vs неправильно |
| **Обратная совместимость** | Conventional Commits работают как раньше |

---

## Метрики для analyzer.py

Теперь analyzer.py сможет показать:

```python
{
    "total_commits": 100,
    "by_type": {
        "feat": 25,
        "fix": 20,
        "non-conventional": 55  # ← Видно сколько коммитов без формата
    }
}
```

---

## Следующий шаг

**analyzer.py**

Используем обновлённый parser_service.py для анализа всех коммитов в репозитории.
