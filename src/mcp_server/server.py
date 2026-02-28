"""Git Changelog MCP Server implementation."""

from fastmcp import FastMCP
from starlette.responses import JSONResponse

mcp = FastMCP("Git Changelog")


@mcp.custom_route("/health", methods=["GET"])
def health_check(request):
    """Health check endpoint for monitoring and load balancers."""
    return JSONResponse({"status": "healthy", "service": "git-changelog-mcp"})


@mcp.tool()
def analyze_commits(
    repo_path: str,
    from_ref: str | None = None,
    to_ref: str | None = None,
) -> dict:
    """
    Analyze commits in a git repository.
    
    Args:
        repo_path: Path to the git repository
        from_ref: Starting reference (branch, tag, commit)
        to_ref: Ending reference (branch, tag, commit)
        
    Returns:
        Dictionary with commit analysis results
    """
    return {"status": "not implemented yet"}


@mcp.tool()
def generate_changelog(
    repo_path: str,
    output_format: str = "markdown",
    from_version: str | None = None,
    include_unreleased: bool = True,
) -> str:
    """
    Generate changelog from git history.
    
    Args:
        repo_path: Path to the git repository
        output_format: Output format (markdown, json, keepachangelog)
        from_version: Start from specific version tag (optional)
        include_unreleased: Include unreleased changes (default: True)
        
    Returns:
        Formatted changelog string
    """
    from mcp_server.services.analyzer import analyze_repo
    from mcp_server.services.template_service import TemplateService
    
    # Validate repo_path
    if not repo_path or not isinstance(repo_path, str):
        return "Error: Invalid repo_path"
    
    # Analyze repository
    try:
        result = analyze_repo(repo_path)
    except Exception as e:
        return f"Error: {str(e)}"
    
    # Group commits by version
    ts = TemplateService()
    versions = ts.group_commits_by_version(result['commits'], result['tags'])
    
    # Filter by from_version if specified
    if from_version:
        versions = [v for v in versions if v.version >= from_version]
    
    # Filter unreleased if not included
    if not include_unreleased:
        versions = [v for v in versions if v.version != "Unreleased"]
    
    # Select template
    template_map = {
        "markdown": "changelog.md.j2",
        "md": "changelog.md.j2",
        "json": "changelog.json.j2",
        "keepachangelog": "keepachangelog.md.j2",
        "kal": "keepachangelog.md.j2",
    }
    template_name = template_map.get(output_format.lower(), "changelog.md.j2")
    
    # Render changelog
    try:
        return ts.render_changelog(versions, template_name)
    except Exception as e:
        return f"Error rendering changelog: {str(e)}"


@mcp.tool()
def generate_release_notes(
    repo_path: str,
    version: str,
    style: str = "markdown",
    use_ai: bool = True,
    include_breaking_changes: bool = True,
) -> str:
    """
    Generate release notes for a specific version.

    Args:
        repo_path: Path to the git repository
        version: Version to generate notes for (e.g., 'v1.2.0')
        style: Output style (markdown, brief, detailed)
        use_ai: Use AI generation (requires GITHUB_TOKEN)
        include_breaking_changes: Include breaking changes section

    Returns:
        Formatted release notes string

    Note:
        AI generation requires GITHUB_TOKEN environment variable.
        Falls back to template-based generation if AI unavailable.
    """
    from mcp_server.services.analyzer import analyze_repo
    from mcp_server.services.template_service import TemplateService
    from mcp_server.services.ai import get_ai_client, AIGenerationError, ReleaseNotesStyle
    import logging

    logger = logging.getLogger(__name__)

    # Validate inputs
    if not repo_path or not isinstance(repo_path, str):
        return "Error: Invalid repo_path"
    if not version:
        return "Error: Version is required"

    # Analyze repository
    try:
        result = analyze_repo(repo_path)
    except Exception as e:
        return f"Error analyzing repo: {str(e)}"

    # Get commits for this version
    ts = TemplateService()
    versions = ts.group_commits_by_version(result['commits'], result['tags'])
    
    # Find specific version
    target_version = None
    for v in versions:
        if v.version == version:
            target_version = v
            break
    
    if not target_version:
        available = [v.version for v in versions]
        return f"Error: Version '{version}' not found. Available: {available}"

    # Convert to dict format for AI
    commits_data = []
    for commit in target_version.commits:
        commits_data.append({
            "hash": commit.hash,
            "parsed": {
                "type": commit.type,
                "scope": commit.scope,
                "description": commit.description,
            },
            "breaking": commit.breaking,
            "author": commit.author,
        })

    # Try AI generation if requested
    if use_ai:
        try:
            style_enum = ReleaseNotesStyle(style.lower())
            client = get_ai_client()  # Auto-detect from env
            
            return client.generate_release_notes(
                commits=commits_data,
                version=version,
                style=style_enum,
                language="ru"
            )
        except AIGenerationError as e:
            logger.info(f"AI not available ({e}), falling back to templates")
        except Exception as e:
            logger.warning(f"AI generation failed: {e}, falling back to templates")

    # Fallback: template-based generation
    try:
        # Render single version
        return ts.render_changelog([target_version], "release_notes.md.j2")
    except Exception as e:
        return f"Error generating release notes: {str(e)}"


def main() -> None:
    """Run the MCP server with Streamable HTTP transport."""
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )


if __name__ == "__main__":
    main()
