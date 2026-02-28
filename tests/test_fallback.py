#!/usr/bin/env python3
"""Test fallback without token."""

import os
from mcp_server.server import generate_release_notes

# Временно убираем токен
if "GITHUB_TOKEN" in os.environ:
    del os.environ["GITHUB_TOKEN"]

print("=" * 60)
print("ТЕСТ: generate_release_notes БЕЗ токена (fallback)")
print("=" * 60)

result = generate_release_notes(
    repo_path="demo_project",
    version="v1.2.0",
    use_ai=True,  # Пытаемся использовать AI
    style="markdown"
)

print("\n✅ Результат:")
print(result[:1000])  # Первые 1000 символов
print("\n...")
print(f"\n✅ Длина: {len(result)} символов")

# Проверяем что это шаблон (fallback)
if "New Features" in result or "Bug Fixes" in result:
    print("✅ Fallback на шаблоны работает!")
else:
    print("⚠️ Что-то пошло не так")
