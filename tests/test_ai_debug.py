#!/usr/bin/env python3
"""Debug AI generation."""

import os
import logging

# Включаем логирование
logging.basicConfig(level=logging.DEBUG)

from mcp_server.server import generate_release_notes
from mcp_server.services.ai import get_ai_client, AIGenerationError

print("=" * 60)
print("DEBUG: Проверка AI клиента")
print("=" * 60)

# Проверяем токен
token = os.getenv("GITHUB_TOKEN")
print(f"\n✅ GITHUB_TOKEN: {token[:20] if token else 'None'}...")

# Пытаемся создать клиента
try:
    print("\n🔄 Создаём GitHubClient...")
    client = get_ai_client()
    print(f"✅ Клиент создан: {type(client).__name__}")
    print(f"✅ Model: {client.model}")
    print(f"✅ Base URL: {client.base_url}")
except AIGenerationError as e:
    print(f"❌ Ошибка: {e}")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")

# Тестируем генерацию
print("\n" + "=" * 60)
print("ТЕСТ: generate_release_notes")
print("=" * 60)

result = generate_release_notes(
    repo_path="demo_project",
    version="v1.2.0",
    use_ai=True,
    style="markdown"
)

print(f"\n✅ Результат ({len(result)} символов):")
print(result[:500])
