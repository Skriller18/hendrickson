from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.models.settings import (
    GitHubSettings,
    JIRASettings,
    LinearSettings,
    ProviderKey,
    UserSettings,
)

router = APIRouter()


class ProviderKeyRequest(BaseModel):
    provider: str
    api_key: str
    label: str = ""


class JIRAConfigRequest(BaseModel):
    url: str
    email: str
    api_token: str


class LinearConfigRequest(BaseModel):
    api_key: str


class GitHubConfigRequest(BaseModel):
    token: str


async def _get_settings(db) -> UserSettings:
    doc = await db.settings.find_one({"settings_id": "default"})
    if not doc:
        return UserSettings()
    doc.pop("_id", None)
    return UserSettings(**doc)


async def _save_settings(db, settings: UserSettings):
    from datetime import datetime
    settings.updated_at = datetime.utcnow()
    await db.settings.replace_one(
        {"settings_id": "default"},
        settings.model_dump(),
        upsert=True,
    )


@router.get("/")
async def get_settings(request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    return settings.model_dump()


@router.post("/provider-keys")
async def add_provider_key(req: ProviderKeyRequest, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)

    existing = [k for k in settings.provider_keys if k.provider != req.provider]
    existing.append(ProviderKey(provider=req.provider, api_key=req.api_key, label=req.label))
    settings.provider_keys = existing

    await _save_settings(db, settings)
    return {"status": "ok", "provider": req.provider}


@router.delete("/provider-keys/{provider}")
async def remove_provider_key(provider: str, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    settings.provider_keys = [k for k in settings.provider_keys if k.provider != provider]
    await _save_settings(db, settings)
    return {"status": "ok"}


@router.post("/jira")
async def configure_jira(req: JIRAConfigRequest, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    settings.connectors.jira = JIRASettings(url=req.url, email=req.email, api_token=req.api_token)
    await _save_settings(db, settings)
    return {"status": "ok"}


@router.post("/linear")
async def configure_linear(req: LinearConfigRequest, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    settings.connectors.linear = LinearSettings(api_key=req.api_key)
    await _save_settings(db, settings)
    return {"status": "ok"}


@router.post("/github")
async def configure_github(req: GitHubConfigRequest, request: Request):
    import httpx

    db = request.app.state.mongo_db
    settings = await _get_settings(db)

    username = ""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {req.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            if resp.status_code == 200:
                username = resp.json().get("login", "")
    except Exception:
        pass

    settings.connectors.github = GitHubSettings(
        token=req.token,
        connected=bool(username),
        username=username,
    )
    await _save_settings(db, settings)
    return {"status": "ok", "username": username, "connected": bool(username)}


@router.delete("/github")
async def disconnect_github(request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    settings.connectors.github = GitHubSettings()
    await _save_settings(db, settings)
    return {"status": "ok"}


@router.post("/default-model")
async def set_default_model(model: str, request: Request):
    db = request.app.state.mongo_db
    settings = await _get_settings(db)
    settings.default_model = model
    await _save_settings(db, settings)
    return {"status": "ok"}
