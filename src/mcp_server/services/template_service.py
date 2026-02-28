"""Template Service for changelog generation."""

from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import List

from ..models.changelog import ChangelogVersion


class TemplateService:
    """Service for rendering changelog templates."""
    
    def __init__(self, template_dir: str | None = None):
        """
        Initialize template service.

        Args:
            template_dir: Path to templates directory.
                         Default: project root templates/
        """
        if template_dir is None:
            # Project root is 3 levels up from this file:
            # src/mcp_server/services/ -> ../../.. = project root
            project_root = Path(__file__).parent.parent.parent.parent
            template_dir = project_root / "templates"
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['md', 'json']),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add global functions
        self.env.globals['now'] = lambda: datetime.now().isoformat()
    
    def render_changelog(
        self,
        versions: List[ChangelogVersion],
        template_name: str = "changelog.md.j2"
    ) -> str:
        """
        Render changelog from versions.
        
        Args:
            versions: List of ChangelogVersion
            template_name: Template file name
            
        Returns:
            Rendered changelog string
        """
        template = self.env.get_template(template_name)
        return template.render(versions=versions)
    
    def group_commits_by_version(
        self,
        commits: List,  # List[EnrichedCommit] from analyzer
        tags: List[dict]
    ) -> List[ChangelogVersion]:
        """
        Group commits by version tags.

        Commits are grouped by tag ranges:
        - v1.0.0: commits from beginning to v1.0.0
        - v1.1.0: commits between v1.0.0 and v1.1.0
        - v1.2.0: commits between v1.1.0 and v1.2.0
        - Unreleased: commits after the last tag

        Args:
            commits: List of EnrichedCommit from analyzer (newest first)
            tags: List of tag dicts from analyzer (name, date, hash)

        Returns:
            List of ChangelogVersion, sorted by date (newest first)
        """
        from ..models.changelog import ChangelogCommit

        if not tags:
            # No tags - all commits are unreleased
            return self._create_unreleased_version(commits)

        # Sort tags by date (oldest first)
        sorted_tags = sorted(tags, key=lambda t: t['date'])

        versions = []

        # Create version for each tag
        for i, tag in enumerate(sorted_tags):
            version = ChangelogVersion(
                version=tag['name'],
                date=tag['date'].strftime('%Y-%m-%d') if hasattr(tag['date'], 'strftime') else str(tag['date'])
            )

            # Determine commit range for this version
            if i == 0:
                # First tag: all commits up to and including this tag
                version_commits = [
                    c for c in commits
                    if c.date <= tag['date']
                ]
            else:
                # Subsequent tags: commits between previous and current tag
                prev_tag = sorted_tags[i - 1]
                version_commits = [
                    c for c in commits
                    if prev_tag['date'] < c.date <= tag['date']
                ]

            # Add commits to version
            for commit in version_commits:
                changelog_commit = ChangelogCommit(
                    hash=commit.hash,
                    short_hash=commit.short_hash,
                    type=commit.parsed.type,
                    scope=commit.parsed.scope,
                    description=commit.parsed.description,
                    breaking=commit.parsed.breaking,
                    author=commit.author,
                    date=commit.date
                )
                version.add_commit(changelog_commit)

            # Only add version if it has commits
            if version.commits:
                versions.append(version)

        # Add unreleased commits (after the last tag)
        last_tag = sorted_tags[-1]
        unreleased_commits = [
            c for c in commits
            if c.date > last_tag['date']
        ]

        if unreleased_commits:
            unreleased = ChangelogVersion(
                version="Unreleased",
                date=None  # Will be handled by template
            )
            for commit in unreleased_commits:
                changelog_commit = ChangelogCommit(
                    hash=commit.hash,
                    short_hash=commit.short_hash,
                    type=commit.parsed.type,
                    scope=commit.parsed.scope,
                    description=commit.parsed.description,
                    breaking=commit.parsed.breaking,
                    author=commit.author,
                    date=commit.date
                )
                unreleased.add_commit(changelog_commit)
            versions.append(unreleased)

        # Reverse to get newest first (standard changelog order)
        versions.reverse()

        return versions

    def _create_unreleased_version(
        self,
        commits: List
    ) -> List[ChangelogVersion]:
        """
        Create a single unreleased version from commits.
        
        Used when there are no tags in the repository.
        """
        from ..models.changelog import ChangelogCommit
        
        if not commits:
            return []
        
        unreleased = ChangelogVersion(
            version="Unreleased",
            date=None
        )
        
        for commit in commits:
            changelog_commit = ChangelogCommit(
                hash=commit.hash,
                short_hash=commit.short_hash,
                type=commit.parsed.type,
                scope=commit.parsed.scope,
                description=commit.parsed.description,
                breaking=commit.parsed.breaking,
                author=commit.author,
                date=commit.date
            )
            unreleased.add_commit(changelog_commit)
        
        return [unreleased]
