from mcp_server.services.analyzer import analyze_repo
from mcp_server.services.template_service import TemplateService
result = analyze_repo('demo_project')
ts = TemplateService()
versions = ts.group_commits_by_version(result['commits'], result['tags'])
print("=" * 80)
print("CHANGELOG (markdown)")
print("=" * 80)
md = ts.render_changelog(versions, "keepachangelog.md.j2")
print(md)