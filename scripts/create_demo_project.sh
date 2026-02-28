#!/bin/bash
# Script to create demo_project with conventional commits
# Usage: bash scripts/create_demo_project.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../demo_project"

echo "🔧 Creating demo_project..."

# Remove existing demo_project if exists
rm -rf "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

cd "$PROJECT_DIR"

# Initialize git repo
git init
git config user.email "demo@example.com"
git config user.name "Demo User"

# Create initial files
echo '# Demo Project

Test repository for Git Changelog MCP Server.

## Version History

- **v1.0.0** — Initial release with basic features
- **v1.1.0** — API improvements and bug fixes
- **v1.2.0** — Latest features (rate limiting, CSV export)
' > README.md

echo '[project]
name = "demo-project"
version = "1.2.0"
description = "Demo project for Git Changelog MCP Server testing"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
' > pyproject.toml

mkdir -p src tests

echo '"""Main application module."""


def greet(name: str) -> str:
    """Return greeting message."""
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
' > src/app.py

echo '"""Tests for app module."""

from src.app import greet, add


def test_greet() -> None:
    """Test greet function."""
    assert greet("World") == "Hello, World!"


def test_add() -> None:
    """Test add function."""
    assert add(2, 3) == 5
' > tests/test_app.py

echo "# Demo project files" > .gitignore

# Commit 1: Initial commit
git add .
GIT_AUTHOR_DATE="2026-02-28T09:00:00" GIT_COMMITTER_DATE="2026-02-28T09:00:00" git commit -m "feat: initial commit"

echo "📝 Creating git history..."

# Commit 2: feat(api)
echo "# Auth module" > src/auth.py
git add src/auth.py
GIT_AUTHOR_DATE="2026-02-28T09:30:00" GIT_COMMITTER_DATE="2026-02-28T09:30:00" git commit -m "feat(api): add user authentication"

# Commit 3: fix(ui)
echo "# UI styles" > src/styles.css
git add src/styles.css
GIT_AUTHOR_DATE="2026-02-28T09:45:00" GIT_COMMITTER_DATE="2026-02-28T09:45:00" git commit -m "fix(ui): resolve button alignment issue"

# Commit 4: docs
echo "# API Documentation" > docs.md
git add docs.md
GIT_AUTHOR_DATE="2026-02-28T09:55:00" GIT_COMMITTER_DATE="2026-02-28T09:55:00" git commit -m "docs: update README with API documentation"

# TAG v1.0.0
GIT_COMMITTER_DATE="2026-02-28T10:00:00" git tag -a v1.0.0 -m "Release v1.0.0 - Initial release"
echo "📦 Created tag v1.0.0 (2026-02-28 10:00:00)"

# Commit 5: feat with emoji (dark mode)
echo "# Dark mode styles" >> src/styles.css
git add src/styles.css
GIT_AUTHOR_DATE="2026-02-28T11:00:00" GIT_COMMITTER_DATE="2026-02-28T11:00:00" git commit -m "feat(ui): add dark mode support"

# Commit 6: feat! (breaking change)
echo "# New API v2" > src/api_v2.py
git add src/api_v2.py
GIT_AUTHOR_DATE="2026-02-28T12:00:00" GIT_COMMITTER_DATE="2026-02-28T12:00:00" git commit -m "feat(api)!: remove deprecated v1 API endpoints"

# Commit 7: fix(auth)
echo "# Auth fixes" >> src/auth.py
git add src/auth.py
GIT_AUTHOR_DATE="2026-02-28T13:00:00" GIT_COMMITTER_DATE="2026-02-28T13:00:00" git commit -m "fix(auth): handle edge case in login flow"

# Commit 8: refactor(core)
echo "# Optimized queries" > src/database.py
git add src/database.py
GIT_AUTHOR_DATE="2026-02-28T14:00:00" GIT_COMMITTER_DATE="2026-02-28T14:00:00" git commit -m "refactor(core): optimize database queries"

# Commit 9: test
echo "# Integration tests" > tests/test_integration.py
git add tests/test_integration.py
GIT_AUTHOR_DATE="2026-02-28T15:00:00" GIT_COMMITTER_DATE="2026-02-28T15:00:00" git commit -m "test: add integration tests for API endpoints"

# Commit 10: chore
echo "# Dependencies updated" >> README.md
git add README.md
GIT_AUTHOR_DATE="2026-02-28T16:00:00" GIT_COMMITTER_DATE="2026-02-28T16:00:00" git commit -m "chore: update dependencies to latest versions"

# TAG v1.1.0
GIT_COMMITTER_DATE="2026-02-28T16:30:00" git tag -a v1.1.0 -m "Release v1.1.0 - API improvements"
echo "📦 Created tag v1.1.0 (2026-02-28 16:30:00)"

# Commit 11: non-conventional commit (without conventional format)
echo "# Some quick fix" > src/quick_fix.py
git add src/quick_fix.py
GIT_AUTHOR_DATE="2026-02-28T17:00:00" GIT_COMMITTER_DATE="2026-02-28T17:00:00" git commit -m "quick fix for production issue"

# Commit 12: feat(api) - rate limiting
echo "# Rate limiting middleware" > src/rate_limit.py
git add src/rate_limit.py
GIT_AUTHOR_DATE="2026-02-28T17:30:00" GIT_COMMITTER_DATE="2026-02-28T17:30:00" git commit -m "feat(api): add rate limiting middleware"

# Commit 13: non-conventional commit
echo "# Temporary workaround" >> src/app.py
git add src/app.py
GIT_AUTHOR_DATE="2026-02-28T17:45:00" GIT_COMMITTER_DATE="2026-02-28T17:45:00" git commit -m "temporary workaround until proper fix"

# Commit 14: fix with emoji (bug)
echo "# Cache fixes" > src/cache.py
git add src/cache.py
GIT_AUTHOR_DATE="2026-02-28T18:00:00" GIT_COMMITTER_DATE="2026-02-28T18:00:00" git commit -m "fix(cache): fix memory leak in cache layer"

# Commit 15: docs(api)
echo "# API Reference" > API.md
git add API.md
GIT_AUTHOR_DATE="2026-02-28T18:30:00" GIT_COMMITTER_DATE="2026-02-28T18:30:00" git commit -m "docs(api): add comprehensive API documentation"

# Commit 16: ci
mkdir -p .github/workflows
echo "# CI workflow" > .github/workflows/ci.yml
git add .github/workflows/ci.yml
GIT_AUTHOR_DATE="2026-02-28T19:00:00" GIT_COMMITTER_DATE="2026-02-28T19:00:00" git commit -m "ci: add GitHub Actions CI/CD workflow"

# Commit 17: feat (CSV export)
echo "# CSV export feature" >> src/app.py
git add src/app.py
GIT_AUTHOR_DATE="2026-02-28T19:30:00" GIT_COMMITTER_DATE="2026-02-28T19:30:00" git commit -m "feat: add export to CSV feature"

# TAG v1.2.0
GIT_COMMITTER_DATE="2026-02-28T19:30:00" git tag -a v1.2.0 -m "Release v1.2.0 - Latest features"
echo "📦 Created tag v1.2.0 (2026-02-28 19:30:00)"

echo ""
echo "✅ Git history created successfully!"
echo ""
echo "📊 Summary:"
echo "   - 17 commits"
echo "   - 3 tags (v1.0.0, v1.1.0, v1.2.0)"
echo "   - 1 breaking change"
echo "   - 2 non-conventional commits"
echo ""
echo "📝 Commit types:"
echo "   - feat: 6"
echo "   - fix: 3"
echo "   - docs: 2"
echo "   - refactor: 1"
echo "   - test: 1"
echo "   - chore: 1"
echo "   - ci: 1"
echo "   - non-conventional: 2"
