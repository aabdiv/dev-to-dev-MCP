"""Changelog models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class ChangelogCommit:
    """Commit for changelog rendering."""
    hash: str
    short_hash: str
    type: str
    scope: str | None
    description: str
    breaking: bool
    author: str
    date: datetime


@dataclass
class ChangelogVersion:
    """Version entry in changelog."""
    version: str
    date: str
    commits: List[ChangelogCommit] = field(default_factory=list)
    breaking_changes: List[ChangelogCommit] = field(default_factory=list)
    commits_by_type: Dict[str, List[ChangelogCommit]] = field(default_factory=dict)
    
    def add_commit(self, commit: ChangelogCommit) -> None:
        """Add commit to version."""
        self.commits.append(commit)
        
        if commit.breaking:
            self.breaking_changes.append(commit)
        
        if commit.type not in self.commits_by_type:
            self.commits_by_type[commit.type] = []
        self.commits_by_type[commit.type].append(commit)
