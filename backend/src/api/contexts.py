import uuid
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from src.engines.triangulator import Triangulator
from src.config import settings

router = APIRouter()


class TriangulateRequest(BaseModel):
    prd_content: str | None = None
    prd_path: str | None = None
    repo_url: str | None = None
    branch: str = "main"
    jira_keys: list[str] | None = None
    linear_issue_ids: list[str] | None = None


class ContextResponse(BaseModel):
    context_id: str
    requirements: list[dict]
    code_entities: list[dict]
    tickets: list[dict]
    codebase: dict | None = None


async def _get_user_settings(db):
    doc = await db.settings.find_one({"settings_id": "default"})
    if not doc:
        return None
    doc.pop("_id", None)
    return doc


@router.post("/triangulate", response_model=ContextResponse)
async def triangulate(req: TriangulateRequest, request: Request):
    db = request.app.state.mongo_db
    user_settings = await _get_user_settings(db)

    github_token = settings.github_token
    jira_url = settings.jira_url
    jira_email = settings.jira_email
    jira_api_token = settings.jira_api_token
    linear_api_key = settings.linear_api_key

    if user_settings:
        conn = user_settings.get("connectors", {})
        github_token = conn.get("github", {}).get("token") or github_token
        jira_url = conn.get("jira", {}).get("url") or jira_url
        jira_email = conn.get("jira", {}).get("email") or jira_email
        jira_api_token = conn.get("jira", {}).get("api_token") or jira_api_token
        linear_api_key = conn.get("linear", {}).get("api_key") or linear_api_key

    triangulator = Triangulator(
        github_token=github_token,
        jira_url=jira_url,
        jira_email=jira_email,
        jira_api_token=jira_api_token,
        linear_api_key=linear_api_key,
    )

    result = await triangulator.triangulate(
        prd_path=req.prd_path,
        prd_content=req.prd_content,
        repo_url=req.repo_url,
        branch=req.branch,
        jira_keys=req.jira_keys,
        linear_issue_ids=req.linear_issue_ids,
    )

    context_doc = triangulator.build_context_document(result)

    vector_store = request.app.state.vector_store

    await db.contexts.insert_one(context_doc.model_dump())

    requirements = result.get("requirements", [])
    if requirements:
        for req in requirements:
            req["context_id"] = result["context_id"]
            req["requirement_id"] = req.get("tag", f"REQ-{uuid.uuid4().hex[:6].upper()}")
        await db.requirements.insert_many(requirements)
        await vector_store.index_requirements(requirements)

    code_entities = result.get("code_entities", [])
    if code_entities:
        for ent in code_entities:
            ent["context_id"] = result["context_id"]
            ent["entity_id"] = f"ENT-{uuid.uuid4().hex[:6].upper()}"
        await db.code_entities.insert_many(code_entities)
        await vector_store.index_code_entities(code_entities)

    tickets = result.get("tickets", [])
    if tickets:
        for ticket in tickets:
            ticket["context_id"] = result["context_id"]
            ticket["ticket_id"] = f"TKT-{uuid.uuid4().hex[:6].upper()}"
        await db.tickets.insert_many(tickets)

    return ContextResponse(
        context_id=result["context_id"],
        requirements=requirements,
        code_entities=code_entities,
        tickets=tickets,
        codebase=result.get("codebase"),
    )


@router.get("/{context_id}")
async def get_context(context_id: str, request: Request):
    db = request.app.state.mongo_db
    doc = await db.contexts.find_one({"context_id": context_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Context not found")
    doc.pop("_id", None)
    return doc


@router.get("/")
async def list_contexts(request: Request):
    db = request.app.state.mongo_db
    cursor = db.contexts.find().sort("created_at", -1).limit(20)
    contexts = []
    async for doc in cursor:
        doc.pop("_id", None)
        contexts.append(doc)
    return contexts
