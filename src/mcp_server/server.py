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
    include_breaking_changes: bool = True,
) -> str:
    """
    Generate release notes for a specific version.
    
    Args:
        repo_path: Path to the git repository
        version: Version to generate notes for (e.g., 'v1.2.0')
        style: Output style (markdown, brief, detailed)
        include_breaking_changes: Include breaking changes section
        
    Returns:
        Formatted release notes string
    """
    return f"# Release Notes\n\nNot implemented yet"


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
