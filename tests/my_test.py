from mcp_server.services.analyzer import analyze_repo
from mcp_server.services.template_service import TemplateService
result = analyze_repo('demo_project')
# result = analyze_repo('/Users/vadimv/code/Python/fastapi_tutorial')
ts = TemplateService()
versions = ts.group_commits_by_version(result['commits'], result['tags'])
print("=" * 80)
print("CHANGELOG (markdown)")
print("=" * 80)
md = ts.render_changelog(versions, "changelog.md.j2")
with open('./tests/my_md.md', 'w') as file_out:
    print(md, file=file_out)