"""Conventional Commits Parser Service.

Parses commit messages in Conventional Commits format.
Non-conventional commits are also supported (type='non-conventional').
"""

import re
from dataclasses import dataclass


# Constants
COMMIT_TYPES = {
    "feat", "fix", "perf", "refactor", "docs", "test", "style", "chore", "build", "ci", "revert"
}

NON_CONVENTIONAL_TYPE = "non-conventional"

WIP_PATTERNS = ["WIP:", "wip:", "Draft:", "DO NOT MERGE"]


@dataclass
class ParsedCommit:
    """Parsed commit structure."""
    type: str
    description: str
    scope: str | None = None
    breaking: bool = False
    body: str | None = None
    raw: str = ""


# Regex patterns
MAIN_PATTERN = re.compile(
    r'^(?P<type>feat|fix|perf|refactor|docs|test|style|chore|build|ci|revert)'
    r'(\((?P<scope>[\w\-]+)\))?'
    r'(?P<breaking>!)?:\s*'
    r'(?P<description>.+)$'
)

BREAKING_PATTERN = re.compile(
    r'^(?:BREAKING\s+CHANGE|BREAKING):\s*(?P<description>.+)$',
    re.MULTILINE
)


def parse_commit(message: str) -> ParsedCommit | None:
    """
    Parse a commit message in Conventional Commits format.
    
    Non-conventional commits are also parsed with type='non-conventional'.
    WIP commits and empty messages return None (intentionally skipped).
    
    Args:
        message: Raw commit message (full with body)
        
    Returns:
        ParsedCommit or None if WIP or empty
        
    Example:
        >>> parse_commit("feat(api): add auth")
        ParsedCommit(type='feat', scope='api', description='add auth', breaking=False)
        
        >>> parse_commit("feat!: remove API")
        ParsedCommit(type='feat', scope=None, description='remove API', breaking=True)
        
        >>> parse_commit("fixed stuff")
        ParsedCommit(type='non-conventional', description='fixed stuff', breaking=False)
        
        >>> parse_commit("WIP: working on it")
        None
    """
    if _is_wip(message):
        return None
    
    # Split header and body
    lines = message.strip().split('\n', 1)
    header = lines[0].strip()
    body = lines[1].strip() if len(lines) > 1 else ""
    
    # Empty message
    if not header:
        return None
    
    # Apply Conventional Commits regex
    match = MAIN_PATTERN.match(header)
    if match:
        # Conventional commit
        breaking = match.group('breaking') == '!' or _extract_breaking_change(body)
        
        return ParsedCommit(
            type=match.group('type'),
            description=match.group('description'),
            scope=match.group('scope'),
            breaking=breaking,
            body=body if body else None,
            raw=message.strip()
        )
    
    # Non-conventional commit
    return ParsedCommit(
        type=NON_CONVENTIONAL_TYPE,
        description=header,
        scope=None,
        breaking=False,
        body=body if body else None,
        raw=message.strip()
    )


def _is_wip(message: str) -> bool:
    """
    Check if message is WIP.
    
    Only checks the beginning of the header, not the entire message.
    This prevents false positives like "feat: add WIP tracking" being treated as WIP.
    """
    header = message.split('\n')[0].strip().lower()
    return any(
        header.startswith(pattern.lower())
        for pattern in ["WIP:", "wip:", "draft:", "do not merge"]
    )


def _extract_breaking_change(body: str) -> bool:
    """Extract BREAKING CHANGE from body."""
    return bool(BREAKING_PATTERN.search(body))
