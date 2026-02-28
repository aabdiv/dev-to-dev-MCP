# 🎬 Демонстрация Git Changelog MCP Server

---

## 📋 Подготовка

### Ключевые предусловия (помимо запуска контейнера и MCP Inspector)
- [ ] Скрипт создания demo_project выполнен
```bash
chmod +x scripts/create_demo_project.sh
bash scripts/create_demo_project.sh
```
> Демо-репозиторий создается отдельно скриптом, а не хранится в общем репозитории (как прописано в критериях) 
> Причина - для демонстрации в самом демо-репозитории требуется наличие своих коммитов и тэгов (то есть вложенный демо-репозиторий должен быть репозиторием git),
> а вложенность git-репозиториев мешает воспроизводимости 

- [ ] На этапе запуска демо-директория правильно монтирована в контейнер
```bash
docker run -p 8000:8000 -v $(pwd)/demo_project:/app/project git-changelog-mcp serve
``` 

<details>
<summary>Быстрый старт (нажмите чтобы открыть)</summary>

```bash
# 1. Сборка образа
docker build -t git-changelog-mcp .

# Готовый образ также можно скачать из DockerHub
docker pull aabdiv/git-changelog-mcp:latest
docker tag aabdiv/git-changelog-mcp:latest git-changelog-mcp:latest
docker rmi aabdiv/git-changelog-mcp:latest

# 2. Создание demo_project если отсутствует
bash scripts/create_demo_project.sh

# 3. Запуск сервера
docker run -p 8000:8000 \
  -v $(pwd)/demo_project:/app/project \
  git-changelog-mcp serve

# 4. Проверка готовности
curl http://localhost:8000/health
# Ожидается: {"status": "healthy", "service": "git-changelog-mcp"}

# 5. Запуск MCP Inspector (отдельный терминал)
npx @modelcontextprotocol/inspector
```
</details>

---
---
---

## 🎯 Сценарий 1: Автоматическая генерация CHANGELOG

**📌 Проблема:** 
- Вручную писать changelog для релиза — долго 
- При написании вручную можно пропустить важные детали
- Сложно вернуться к заброшенному проекту
**✨ Решение:** Tool `generate_changelog` автоматически анализирует git-историю

### Шаг 1: Подключение MCP Inspector

<img src="docs/images/inspector1.png" width="400" alt="Описание">

### Шаг 2: Выбор инструмента 

- На вкладке **Tools** найти `generate_changelog`

### Шаг 3: Параметры

| Поле | Значение | Варианты |
|------|----------|-------------|
| `repo_path` | `/app/project` |
| `output_format` | `markdown` |  `markdown`, `json`, `keepachangelog`
| `from_version` | `null` (default) | `v1.1.0`
| `include_unreleased` | `true` |

**Кнопка:** **Run Tool**


## Шаг 4: Примеры вывода 📂 

<details>
<summary><strong>output_format=markdown, from_version=null, include_uncreleased=true (нажмите чтобы открыть)</strong></summary>

---

# Changelog
## Unreleased
*2 commits, 0 breaking changes*
### Fix
- resolve memory leak in cache layer (Demo User, [`11fb42f`](11fb42fc5d56af34473c052c01e0964b71718743))
### Perf
- optimize database queries for better performance (Demo User, [`4bf29af`](4bf29afb59b86e5aa65425e5b7623261c9c10c1c))
### 👥 Contributors
Thanks to: @Demo User (2 commits)
## v1.2.0 (2026-02-28)
*7 commits, 0 breaking changes*
### Feat
- add export to CSV feature (Demo User, [`ad0edb6`](ad0edb64da9f9e7ec514aff300ceeba73d644cb3))
- add rate limiting middleware (**api**) (Demo User, [`f264c6c`](f264c6cafc78d3eb74b85f350e4d11c348b1818c))
### Ci
- add GitHub Actions CI/CD workflow (Demo User, [`bab5b2f`](bab5b2f9d26f7ae67512562c0a948250577b3dfd))
### Docs
- add comprehensive API documentation (**api**) (Demo User, [`081b08d`](081b08dcdba54eebaf762125390ac73147c0749e))
### Fix
- fix memory leak in cache layer (**cache**) (Demo User, [`0beb640`](0beb640fd2d284183df961e44d7e5e9d402931a6))
### Other Changes
- temporary workaround until proper fix (Demo User, [`3e1ffb5`](3e1ffb564e9cb84242fd158d2e6d80f1e2f487b7))
- quick fix for production issue (Demo User, [`0d6dd1b`](0d6dd1b59ed95834d0a9352958b818713b46de1f))
### 👥 Contributors
Thanks to: @Demo User (7 commits)
## v1.1.0 (2026-02-28)
*6 commits, 1 breaking changes*
### ⚠️ Breaking Changes
- **feat(api)**: remove deprecated v1 API endpoints (Demo User, [`281ee78`](281ee78e0c327c98ceb14c60250210ca4210f49b))
### Chore
- update dependencies to latest versions (Demo User, [`ea7b0d3`](ea7b0d3bd543497b71575bfd2205a421bcd233f0))
### Test
- add integration tests for API endpoints (Demo User, [`83ebaa6`](83ebaa61301978734890a63315c656ec3d7782e5))
### Refactor
- optimize database queries (**core**) (Demo User, [`d44d8a5`](d44d8a58ccddcf3017ea8cc238a761142619a6c1))
### Fix
- handle edge case in login flow (**auth**) (Demo User, [`7515541`](75155419e503da15dc3230df98b43d8d518dfaa6))
### Feat
- remove deprecated v1 API endpoints (**api**) (Demo User, [`281ee78`](281ee78e0c327c98ceb14c60250210ca4210f49b))
- add dark mode support (**ui**) (Demo User, [`d2eaad8`](d2eaad8c2f266ee6cc50930c5a855894098fd600))
### 👥 Contributors
Thanks to: @Demo User (6 commits)
## v1.0.0 (2026-02-28)
*4 commits, 0 breaking changes*
### Docs
- update README with API documentation (Demo User, [`75b9ed9`](75b9ed986aff0c519ad523f114aae19c497e4af4))
### Fix
- resolve button alignment issue (**ui**) (Demo User, [`7c56636`](7c56636f6239e5606257a2d5498efee4d7b2185b))
### Feat
- add user authentication (**api**) (Demo User, [`1887ece`](1887ece39a0982110f66f186801ea4db23a15723))
- initial commit (Demo User, [`da3a4ce`](da3a4ce0a686b2e9b5aed1c1cecf1417d6da88e3))
### 👥 Contributors
Thanks to: @Demo User (4 commits)

---

</details>

<details>
<summary><strong>output_format=json, from_version=v1.2.0, include_uncreleased=false (нажмите чтобы открыть)</strong></summary>

---

```json
{
  "metadata": {
    "generator": "git-changelog-mcp",
    "version": "0.1.0",
    "generated_at": "2026-02-28T20:38:30.415680",
    "format": "keepachangelog-json"
  },
  "changelog": [
    {
      "version": "v1.2.0",
      "date": "2026-02-28",
      "stats": {
        "total_commits": 7,
        "breaking_changes": 0,
        "contributors": 1
      },
      "breaking_changes": [],
      "changes": {
        "feat": [
          {
            "type": "feat",
            "description": "add export to CSV feature",
            "scope": null,
            "author": "Demo User",
            "hash": "ad0edb6",
            "breaking": false
          },
          {
            "type": "feat",
            "description": "add rate limiting middleware",
            "scope": "api",
            "author": "Demo User",
            "hash": "f264c6c",
            "breaking": false
          }
        ],
        "ci": [
          {
            "type": "ci",
            "description": "add GitHub Actions CI/CD workflow",
            "scope": null,
            "author": "Demo User",
            "hash": "bab5b2f",
            "breaking": false
          }
        ],
        "docs": [
          {
            "type": "docs",
            "description": "add comprehensive API documentation",
            "scope": "api",
            "author": "Demo User",
            "hash": "081b08d",
            "breaking": false
          }
        ],
        "fix": [
          {
            "type": "fix",
            "description": "fix memory leak in cache layer",
            "scope": "cache",
            "author": "Demo User",
            "hash": "0beb640",
            "breaking": false
          }
        ],
        "non-conventional": [
          {
            "type": "non-conventional",
            "description": "temporary workaround until proper fix",
            "scope": null,
            "author": "Demo User",
            "hash": "3e1ffb5",
            "breaking": false
          },
          {
            "type": "non-conventional",
            "description": "quick fix for production issue",
            "scope": null,
            "author": "Demo User",
            "hash": "0d6dd1b",
            "breaking": false
          }
        ]
      }
    }
  ]
}
```
---
</details>

---
---
---

## 🎯 Сценарий 2: AI Release Notes 

**📌 Проблема:** Нужно подготовить понятные release notes для команды и соцсетей
**✨ Решение:** Tool `generate_release_notes` с AI-улучшением
<details>
<summary><strong>опциональная AI-интеграция (нажмите чтобы открыть)</strong></summary>

Для включения AI-генерации release notes создайте файл `.env` в корне проекта (можно использоавть образец `.env.example`):

```bash
# .env
GITHUB_TOKEN=ghp_your_token_here
AI_MODEL=gpt-4.1-mini
```
> (MVP тестировался на GitHub Models API, но в `.env.example` можно найти другие)

И передайте переменные при запуске Docker:
```bash
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/demo_project:/app/project \
  git-changelog-mcp serve
```
**Базовая работа не требует переменных!** Будет использован fallback на готовые шаблоны!
</details>

### Шаг 1: Выбор инструмента 

- На вкладке **Tools** найти `generate_release_notes`

### Шаг 2: Параметры


| Поле | Значение | Описание |
|------|----------|----------|
| `repo_path` | `/app/project` | Путь к репозиторию |
| `version` | `v1.2.0` | Версия для release notes - в случае ошибки в ответе будут предложены варианты |
| `style` | `detailed` | Подробный стиль вывода - `brief`, `detailed` |
| `use_ai` | `true` | Включить AI-улучшение |
| `include_breaking_changes` | `true` | Включить секцию breaking changes |

**Кнопка:** **Run Tool**

## Шаг 3: Примеры вывода 📂

<details>
<summary><strong>version=v1.2.0, style=detailed, use_ai=true (нажмите чтобы открыть)</strong></summary>

---
# Release Notes v1.2.0

## ✨ Highlights

- Добавлена возможность экспорта данных в CSV — теперь вы можете быстро выгружать результаты для дальнейшего анализа или отчетности.
- Внедрена middleware для ограничения количества запросов к API, что повышает устойчивость сервиса при пиковых нагрузках.
- Исправлена критическая утечка памяти в кэш-слое, что улучшает стабильность и производительность приложения.

## 🚀 Новые возможности

### Экспорт в CSV

Появилась функция экспорта данных в формате CSV, которая позволяет легко сохранять и обмениваться информацией. Это удобно для пользователей, которым необходимо анализировать данные в привычных инструментах, например, Excel или Google Sheets.

```javascript
// Пример использования экспорта
exportDataToCSV(dataArray, 'report.csv');
```

### Ограничение количества запросов к API (Rate Limiting)

Для повышения надежности и защиты от перегрузок добавлен middleware, который контролирует количество запросов от одного клиента за определенный промежуток времени. Это помогает избежать сбоев и обеспечивает равномерную работу сервиса для всех пользователей.

```javascript
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 минут
  max: 100 // максимум 100 запросов с одного IP
}));
```

### Расширенная документация API

Документация по API была значительно дополнена и теперь содержит подробные описания всех эндпоинтов, параметров и примеров запросов. Это упрощает интеграцию и ускоряет разработку.

## ⚠️ Breaking Changes

В данной версии отсутствуют изменения, нарушающие обратную совместимость.

## 🐛 Исправления багов

- Исправлена утечка памяти в кэш-слое, что позволит избежать падений и повысить общую производительность приложения.
- Временные обходные решения (патчи) внедрены для устранения проблем в продакшене, пока не реализованы полноценные исправления.

## 📊 Статистика

- Количество коммитов: 7
- Основные авторы: команда разработки
- Затронутые области: экспорт данных, API, кэш, CI/CD, документация



Спасибо, что используете нашу платформу! Если у вас есть вопросы или пожелания, не стесняйтесь обращаться к нашей команде поддержки.

---
</details>

<details>
<summary><strong>version=v1.2.0, style=markdown, use_ai=false (FALLBACK) (нажмите чтобы открыть)</strong></summary>

---
# Release Notes: v1.2.0

**Date:** 2026-02-28


## 🚀 New Features

- add export to CSV feature

- add rate limiting middleware (api)


## 🐛 Bug Fixes

- fix memory leak in cache layer (cache)


## 📊 Statistics

- **Commits:** 7
- **Authors:** 1
- **Breaking changes:** 0

---
</details>


---
---
---

## 🎯 Сценарий 3: Smoke Test

**📌 Проблема:** Быстрая проверка работоспособности всего сервера  
**✨ Решение:** Встроенная команда `smoke`


### Шаг 1: Запуск smoke test 

```bash
docker run git-changelog-mcp smoke
```

> **Примечание:** Если образ уже запущен как контейнер, можно выполнить проверку через:
> ```bash
> curl http://localhost:8000/health
> ```

---

### Шаг 2: Проверка 

**Пример ожидаемого вывода:**

```
🏥 Running smoke test...

⏳ Waiting for server to start (max 30s)...
✅ Server started after 2s

🔍 Checking health endpoint...
   HTTP Status: 200
   Response: {"status": "healthy", "service": "git-changelog-mcp"}

✅ Smoke test PASSED (HTTP 200)
```


---
---
---

## 🔧 Troubleshooting

### Проблема: Сервер не запускается

**Симптомы:**
```
Error: Address already in use
```

**Решение:**
```bash
# Остановить существующий контейнер
docker stop demo-mcp 2>/dev/null || true
docker rm demo-mcp 2>/dev/null || true

# Запустить заново на другом порту
docker run -p 8001:8000 \
  -v $(pwd)/demo_project:/app/project \
  git-changelog-mcp serve
```

---

### Проблема: Demo project не найден

**Симптомы:**
```
Error: Repository not found at /app/projects/demo_project
```

**Решение:**
```bash
# 1. Проверить что demo_project существует
ls -la demo_project/.git

# 2. Если отсутствует — создать
bash scripts/create_demo_project.sh

# 3. Проверить, монтирована ли директория в контейнер
docker exec <container_id> ls -la /app/project

# 4. Перезапустить контейнер с правильным volume
docker stop demo-mcp && docker rm demo-mcp
docker run -d --name demo-mcp -p 8000:8000 \
  -v $(pwd)/demo_project:/app/project \
  git-changelog-mcp serve
```

---

### Проблема: AI не работает

**Симптомы:**
- Release notes генерируются без AI-улучшений
- Сообщение "AI provider not configured"

**Решение:**

AI-режим опционален. Для базовой демонстрации можно использовать `use_ai: false`.

Для включения AI создать `.env`:
```bash
# Скопировать пример
cp .env.example .env

# Отредактировать .env (добавить токен)
GITHUB_TOKEN=ghp_your_token_here
AI_MODEL=gpt-4.1-mini

# Перезапустить с переменными
docker stop demo-mcp && docker rm demo-mcp
docker run -d --name demo-mcp -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/demo_project:/app/project \
  git-changelog-mcp serve
```

---

## 📊 Сводная таблица демонстрации

| Сценарий | Инструмент | Ключевой результат |
|----------|------------|-------------------|
| **1. CHANGELOG** | `generate_changelog` | 3 версии, 17 коммитов, группировка |
| **2. Release Notes** | `generate_release_notes` | AI-улучшенные notes с migration guide |
| **3. Smoke Test** | `smoke` (CLI) | ✅ Health check passed |

---

## 🎓 Дополнительные материалы

- [README.md](README.md) — Описание и быстрый старт
- [SPEC.md](SPEC.md) — Техническая спецификация
- [docs/images/](docs/images/) — Скриншоты интерфейса MCP Inspector

---

**🏆 Демонстрация завершена!**

