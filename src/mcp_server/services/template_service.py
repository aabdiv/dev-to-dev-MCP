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
        Group commits by version tags using dates.
        
        Algorithm:
        1. Sort tags by date (newest first)
        2. Iterate commits (newest first)
        3. Commits AFTER newest tag = Unreleased
        4. Commits BETWEEN tags = corresponding version
        5. Commits BEFORE oldest tag = oldest version
        
        Args:
            commits: List of EnrichedCommit from analyzer (newest first)
            tags: List of tag dicts from analyzer (name, date, hash)
            
        Returns:
            List of ChangelogVersion, sorted newest first (Unreleased, v1.2.0, v1.1.0, ...)
        """
        from ..models.changelog import ChangelogCommit
        
        if not tags:
            return self._create_unreleased_version(commits)
        
        # Sort tags newest first
        sorted_tags = sorted(tags, key=lambda t: t['date'], reverse=True)
        
        versions: List[ChangelogVersion] = []
        current_commits: List = []
        tag_index = 0
        
        for commit in commits:
            # Check if we reached a tag boundary (by date)
            while tag_index < len(sorted_tags):
                current_tag = sorted_tags[tag_index]
                tag_date = current_tag['date']
                
                # If commit is at or before tag date, create version boundary
                if commit.date <= tag_date:
                    # Save accumulated commits as Unreleased (only for first tag)
                    if current_commits and tag_index == 0:
                        versions.append(self._create_version_from_commits(
                            current_commits, "Unreleased", None
                        ))
                        current_commits = []
                    
                    # Create version for this tag
                    version = ChangelogVersion(
                        version=current_tag['name'],
                        date=tag_date.strftime('%Y-%m-%d') if hasattr(tag_date, 'strftime') else str(tag_date)
                    )
                    versions.append(version)
                    tag_index += 1
                    break
                else:
                    break
            
            # Add commit to current version
            if versions:
                versions[-1].add_commit(ChangelogCommit(
                    hash=commit.hash,
                    short_hash=commit.short_hash,
                    type=commit.parsed.type,
                    scope=commit.parsed.scope,
                    description=commit.parsed.description,
                    breaking=commit.parsed.breaking,
                    author=commit.author,
                    date=commit.date
                ))
            else:
                current_commits.append(commit)
        
        # Handle remaining commits (before oldest tag)
        if current_commits and versions:
            for commit in current_commits:
                versions[-1].add_commit(ChangelogCommit(
                    hash=commit.hash,
                    short_hash=commit.short_hash,
                    type=commit.parsed.type,
                    scope=commit.parsed.scope,
                    description=commit.parsed.description,
                    breaking=commit.parsed.breaking,
                    author=commit.author,
                    date=commit.date
                ))
        
        return versions
    
    def _create_version_from_commits(
        self,
        commits: List,
        version_name: str | None = None,
        date: str | None = None
    ) -> ChangelogVersion:
        """
        Create ChangelogVersion from list of commits.
        
        Args:
            commits: List of EnrichedCommit
            version_name: Version name
            date: Version date
            
        Returns:
            ChangelogVersion with all commits added
        """
        from ..models.changelog import ChangelogCommit
        
        version = ChangelogVersion(
            version=version_name if version_name else "Unreleased",
            date=date
        )
        
        for commit in commits:
            version.add_commit(ChangelogCommit(
                hash=commit.hash,
                short_hash=commit.short_hash,
                type=commit.parsed.type,
                scope=commit.parsed.scope,
                description=commit.parsed.description,
                breaking=commit.parsed.breaking,
                author=commit.author,
                date=commit.date
            ))
        
        return version

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
