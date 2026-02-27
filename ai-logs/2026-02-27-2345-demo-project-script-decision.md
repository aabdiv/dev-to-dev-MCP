# 2026-02-27-2345 — Решение: demo_project как скрипт

**Статус:** ✅ Решение принято  
**Участники:** User (Team Lead), Архитектор  
**Время:** 23:45

---

## Проблема

**Обнаружено:**
```bash
git add demo_project/
# warning: adding embedded git repository: demo_project
# hint: You've added another git repository inside your current repository.
# hint: Clones of the outer repository will not contain the contents of
# hint: the embedded repository and will not know how to obtain it.
```

**Риск:**
- При `git clone` основного репозитория demo_project не будет содержимого
- Проверяющие хакатон не смогут запустить демо-сценарий
- Нарушение требования воспроизводимости

---

## Решение

**Вместо:**
```
❌ demo_project/
   └── .git/  (вложенный репозиторий)
```

**Будет:**
```
✅ scripts/create_demo_project.sh
   └── Создаёт demo_project/ с git-историей при запуске
```

---

## Преимущества

| Преимущество | Описание |
|--------------|----------|
| **Воспроизводимость** | Любой может запустить скрипт и получить demo_project |
| **Контроль** | Полный контроль над содержимым demo_project |
| **Нет вложенности** | Нет проблемы embedded git repository |
| **Документирование** | Скрипт самодокументируем — видно какие коммиты создаются |
| **Гибкость** | Легко изменить содержимое demo_project (поправить скрипт) |

---

## Обновление SPEC.md

**Изменения:**

### 1. Итерация 7: Демо

**Было:**
```markdown
- [ ] scripts/smoke_test.sh
- [ ] End-to-end тесты
- [ ] Демо-сценарий (7 мин)
- [ ] Документация
```

**Стало:**
```markdown
- [ ] scripts/create_demo_project.sh — скрипт создания тестового репозитория
- [ ] scripts/smoke_test.sh — проверка работоспособности
- [ ] End-to-end тесты на созданном demo_project
- [ ] Демо-сценарий (7 мин)
- [ ] Документация (README.md, DEMO.md)
```

### 2. Приоритеты

**Добавлено:**
```markdown
| Компонент | Приоритет | Время |
|-----------|-----------|-------|
| scripts/create_demo_project.sh | MUST | 1ч |
| scripts/smoke_test.sh | MUST | 0.5ч |
```

### 3. Критерии успеха

**Добавлено:**
```markdown
- [ ] scripts/create_demo_project.sh создаёт demo_project за <30 сек
- [ ] demo_project содержит 17 коммитов, 3 тега, 1 breaking change
- [ ] demo_project НЕ вложен в git основного репозитория
```

### 4. Примечание: demo_project

**Добавлено в конец SPEC.md:**
```markdown
## Примечание: demo_project

demo_project НЕ хранится в git основного репозитория.

Для создания тестового проекта:
```bash
bash scripts/create_demo_project.sh
```

Скрипт создаёт:
- 17 коммитов с различными типами (feat, fix, docs, refactor, test, chore, ci)
- 2 non-conventional коммита
- 3 тега (v1.0.0, v1.1.0, v1.2.0)
- 1 breaking change
```

---

## План действий

### 1. Переместить скрипт

```bash
demo_project/init.sh → scripts/create_demo_project.sh
```

### 2. Обновить скрипт

- Создание всей структуры с нуля (README.md, src/, tests/)
- Создание 17 коммитов
- Создание 3 тегов

### 3. Очистить demo_project/

```bash
git rm -r --cached demo_project/
echo "demo_project/" >> .gitignore
```

### 4. Закоммитить

```bash
git add scripts/create_demo_project.sh
git commit -m "feat: Add create_demo_project.sh script"
```

---

## Итог

**Решение:**
- ✅ SPEC.md обновлён
- ✅ scripts/create_demo_project.sh будет создан
- ✅ demo_project/ НЕ вложен в git
- ✅ Воспроизводимость обеспечена

**Следующий шаг:**
Переместить init.sh в scripts/ и обновить скрипт.
