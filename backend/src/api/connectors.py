import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.engines.jira_connector import JIRAConnector
from src.engines.linear_connector import LinearConnector
from src.models.settings import UserSettings

router = APIRouter()


async def _get_settings(db) -> UserSettings:
    doc = await db.settings.find_one({"settings_id": "default"})
    if not doc:
        return UserSettings()
    doc.pop("_id", None)
    return UserSettings(**doc)


class JIRAIssueRequest(BaseModel):
    issue_key: str


class JIRASearchRequest(BaseModel):
    jql: str
    max_results: int = 50


class LinearIssueRequest(BaseModel):
    issue_id: str


class LinearSearchRequest(BaseModel):
    team_id: str
    max_results: int = 50


@router.get("/github/repos")
async def list_github_repos(request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    token = settings.connectors.github.token

    if not token:
        raise HTTPException(status_code=400, detail="GitHub not connected")

    repos = []
    page = 1
    async with httpx.AsyncClient() as client:
        while len(repos) < 100:
            resp = await client.get(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                params={"per_page": 100, "page": page, "sort": "updated"},
            )
            if resp.status_code != 200:
                break
            data = resp.json()
            if not data:
                break
            for repo in data:
                repos.append({
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "private": repo["private"],
                    "html_url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "default_branch": repo.get("default_branch", "main"),
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "updated_at": repo.get("updated_at", ""),
                })
            page += 1

    return repos


@router.get("/github/repos/{owner}/{repo}/branches")
async def list_repo_branches(owner: str, repo: str, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    token = settings.connectors.github.token

    if not token:
        raise HTTPException(status_code=400, detail="GitHub not connected")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/branches",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            params={"per_page": 50},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch branches")

        return [
            {"name": b["name"], "sha": b["commit"]["sha"]}
            for b in resp.json()
        ]


@router.post("/jira/issue")
async def get_jira_issue(req: JIRAIssueRequest, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    jira_cfg = settings.connectors.jira

    if not jira_cfg.url or not jira_cfg.email or not jira_cfg.api_token:
        raise HTTPException(status_code=400, detail="JIRA not configured")

    connector = JIRAConnector(jira_cfg.url, jira_cfg.email, jira_cfg.api_token)
    issue = await connector.get_issue(req.issue_key)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.post("/jira/search")
async def search_jira_issues(req: JIRASearchRequest, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    jira_cfg = settings.connectors.jira

    if not jira_cfg.url or not jira_cfg.email or not jira_cfg.api_token:
        raise HTTPException(status_code=400, detail="JIRA not configured")

    connector = JIRAConnector(jira_cfg.url, jira_cfg.email, jira_cfg.api_token)
    return await connector.search_issues(req.jql, req.max_results)


@router.post("/linear/issue")
async def get_linear_issue(req: LinearIssueRequest, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    linear_cfg = settings.connectors.linear

    if not linear_cfg.api_key:
        raise HTTPException(status_code=400, detail="Linear not configured")

    connector = LinearConnector(linear_cfg.api_key)
    issue = await connector.get_issue(req.issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.get("/linear/teams")
async def list_linear_teams(request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    linear_cfg = settings.connectors.linear

    if not linear_cfg.api_key:
        raise HTTPException(status_code=400, detail="Linear not configured")

    connector = LinearConnector(linear_cfg.api_key)
    return await connector.get_teams()


@router.post("/linear/search")
async def search_linear_issues(req: LinearSearchRequest, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    linear_cfg = settings.connectors.linear

    if not linear_cfg.api_key:
        raise HTTPException(status_code=400, detail="Linear not configured")

    connector = LinearConnector(linear_cfg.api_key)
    return await connector.search_issues(req.team_id, req.max_results)
