import httpx
import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("github-analysis")
GITHUB_API = 'https://api.github.com'

# fetch from github
async def fetch(url: str, token: str = None):
    headers = {
        "User-Agent": "github-analysis/1.0",
        "Accept": "application/vnd.github+json"
    }

    if token:
        headers["Authorization"] = f'Bearer {token}'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None
        
@mcp.tool()
async def get_latest_commit(owner: str, repo: str, token: str = None):
    """
    Fetch and get the details of the most recent commit that the user made in their GitHub repository, including the files changed in the latest commit.

    Args:
        owner: GitHub username or organization
        repo: Repository name
        token: GitHub token for private repository (optional)
    """
    url = f'{GITHUB_API}/repos/{owner}/{repo}/commits'
    
    commits = await fetch(url, token)

    if not commits:
        return f'Could not fetch commits for {owner}/{repo}'
    
    latest_commit = commits[0]
    msg = latest_commit['commit']['message']
    author = latest_commit['commit']['author']['name']
    author_email = latest_commit['commit']['author']['email']
    author_id = latest_commit['author']['id']
    date_commit = latest_commit['commit']['author']['date']
    sha = latest_commit['sha']

    detail_url = f'{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}'
    details = await fetch(detail_url, token)

    changes = ''

    if details and 'files' in details:
        for f in details['files']:
            if f['additions'] != 0 and f['deletions'] != 0:
                changes += f'{f['filename']}:\n+addtions: {f['additions']}\n-deletions: {f['deletions']}\n\n'

    if changes == '':
        changes = 'No details of changed files available'
    
    return f"""
        Latest Commit for {owner}/{repo}:
            Author: {author} - {author_email}
            Date: {date_commit}
            Message: {msg}

            Files Changed:
            {changes}
    """

async def test():
    result = await get_latest_commit("annaznguyn", "portfolio")
    print(result)

if __name__ == "__main__":
    asyncio.run(test())

    # mcp.run(transport="stdio")