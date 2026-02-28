#!/usr/bin/env python3
"""Test AI generation with GitHub token."""

import os
from mcp_server.server import generate_release_notes

# Проверяем что токен установлен
token = os.getenv("GITHUB_TOKEN")
if not token:
    print("❌ GITHUB_TOKEN не установлен!")
    exit(1)

print("=" * 60)
print("ТЕСТ: generate_release_notes С токеном (AI)")
print("=" * 60)
print(f"✅ Токен: {token[:20]}...")
print(f"✅ AI_PROVIDER: {os.getenv('AI_PROVIDER', 'github')}")
print(f"✅ AI_MODEL: {os.getenv('AI_MODEL', 'gpt-4.1-mini')}")
print("=" * 60)

result = generate_release_notes(
    repo_path="demo_project",
    version="v1.2.0",
    use_ai=True,  # Используем AI
    style="markdown"
)

print("\n✅ AI Результат:")
print(result[:1500])  # Первые 1500 символов
print("\n...")
print(f"\n✅ Длина: {len(result)} символов")

# Проверяем что это AI (длинный текст)
if len(result) > 500:
    print("✅ AI генерация работает!")
else:
    print("⚠️ Возможно fallback (короткий текст)")
