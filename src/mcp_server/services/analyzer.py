"""Git Analyzer Service.

Analyzes git repository commits with metadata enrichment.
"""

import os
from dataclasses import dataclass
from datetime import datetime

from git import GitCommandError, Repo

from .parser_service import ParsedCommit, parse_commit


@dataclass
class EnrichedCommit:
    """Commit with metadata from git."""
    parsed: ParsedCommit
    hash: str
    short_hash: str
    author: str
    email: str
    date: datetime
    files_changed: int
    insertions: int
    deletions: int


class InvalidRepoError(Exception):
    """Raised when path is not a git repository."""
    pass


def get_repo(repo_path: str) -> Repo:
    """
    Open git repository with path validation.
    
    Args:
        repo_path: Path to git repository
        
    Returns:
        git.Repo instance
        
    Raises:
        InvalidRepoError: If path is invalid or not a git repository
    """
    # Normalize path to prevent path traversal attacks
    repo_path = os.path.abspath(os.path.normpath(repo_path))
    
    # Check if path exists
    if not os.path.exists(repo_path):
        raise InvalidRepoError(f"Path does not exist: {repo_path}")
    
    # Check if it's a git repository
    if not os.path.exists(os.path.join(repo_path, '.git')):
        raise InvalidRepoError(f"Not a git repository: {repo_path}")
    
    # Try to open
    try:
        return Repo(repo_path)
    except Exception as e:
        raise InvalidRepoError(f"Cannot open repository: {repo_path}") from e


def get_commits_between(
    repo: Repo,
    from_ref: str | None = None,
    to_ref: str | None = None,
) -> list[EnrichedCommit]:
    """
    Extract commits between refs.
    
    Args:
        repo: git.Repo instance
        from_ref: Start ref (tag, branch, commit). Default: None (all commits)
        to_ref: End ref. Default: None (HEAD)
        
    Returns:
        List of EnrichedCommit
        
    Raises:
        InvalidRepoError: If refs are invalid
    """
    # Resolve refs
    if to_ref is None:
        to_ref = "HEAD"
    
    if from_ref is None:
        # All commits to HEAD
        rev_range = to_ref
    else:
        rev_range = f"{from_ref}..{to_ref}"
    
    # Get commits from git with error handling
    try:
        git_commits = list(repo.iter_commits(rev_range))
    except GitCommandError as e:
        raise InvalidRepoError(f"Invalid ref: {rev_range}") from e
    
    # Enrich each commit
    enriched = []
    for commit in git_commits:
        # Parse commit message
        parsed = parse_commit(commit.message)
        
        # Skip WIP commits
        if parsed is None:
            continue
        
        # Get commit stats
        try:
            stats = commit.stats
            files_changed = stats.total_files
            insertions = stats.total_insertions
            deletions = stats.total_deletions
        except Exception:
            files_changed = 0
            insertions = 0
            deletions = 0
        
        # Create enriched commit
        enriched.append(EnrichedCommit(
            parsed=parsed,
            hash=commit.hexsha,
            short_hash=commit.hexsha[:7],
            author=commit.author.name,
            email=commit.author.email,
            date=datetime.fromtimestamp(commit.committed_date),
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        ))
    
    return enriched


def get_tags(repo: Repo) -> list[dict]:
    """
    Get list of annotated tags.
    
    Args:
        repo: git.Repo instance
        
    Returns:
        List of tag info dicts: [{name, hash, date}, ...]
    """
    tags = []
    for tag in repo.tags:
        try:
            # Annotated tag
            tag_date = tag.tag.tagged_date if hasattr(tag, 'tag') and tag.tag else tag.commit.committed_date
            tags.append({
                "name": str(tag),
                "hash": tag.commit.hexsha,
                "date": datetime.fromtimestamp(tag_date),
            })
        except Exception:
            # Lightweight tag
            tags.append({
                "name": str(tag),
                "hash": tag.commit.hexsha,
                "date": datetime.fromtimestamp(tag.commit.committed_date),
            })
    
    # Sort by date
    tags.sort(key=lambda t: t["date"])
    return tags


def aggregate_stats(commits: list[EnrichedCommit]) -> dict:
    """
    Aggregate statistics from commits.
    
    Args:
        commits: List of EnrichedCommit
        
    Returns:
        Dict with aggregated stats
    """
    by_type: dict[str, int] = {}
    by_author: dict[str, int] = {}
    total_files = 0
    total_insertions = 0
    total_deletions = 0
    
    for commit in commits:
        # By type
        commit_type = commit.parsed.type
        by_type[commit_type] = by_type.get(commit_type, 0) + 1
        
        # By author
        author = commit.author
        by_author[author] = by_author.get(author, 0) + 1
        
        # Files/stats
        total_files += commit.files_changed
        total_insertions += commit.insertions
        total_deletions += commit.deletions
    
    return {
        "by_type": by_type,
        "by_author": by_author,
        "files_changed": total_files,
        "insertions": total_insertions,
        "deletions": total_deletions,
    }


def analyze_repo(
    repo_path: str,
    from_ref: str | None = None,
    to_ref: str | None = None,
) -> dict:
    """
    Analyze git repository.
    
    Args:
        repo_path: Path to git repository
        from_ref: Start ref. Default: None (all commits)
        to_ref: End ref. Default: None (HEAD)
        
    Returns:
        Dict with full analysis
    """
    # Open repo
    repo = get_repo(repo_path)
    
    # Get commits
    commits = get_commits_between(repo, from_ref, to_ref)
    
    # Aggregate stats
    stats = aggregate_stats(commits)
    
    # Get tags
    tags = get_tags(repo)
    
    return {
        "repo_path": repo_path,
        "from_ref": from_ref,
        "to_ref": to_ref,
        "commits": commits,
        "summary": {
            "total_commits": len(commits),
            "by_type": stats["by_type"],
            "by_author": stats["by_author"],
        },
        "stats": {
            "files_changed": stats["files_changed"],
            "insertions": stats["insertions"],
            "deletions": stats["deletions"],
        },
        "tags": tags,
    }
