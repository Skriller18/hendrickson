from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient

from src.config import settings
from src.agents.llm_provider import LLMProvider
from src.agents.orchestrator import TestOrchestrator
from src.services.vector_store import VectorStore
from src.api import chat, contexts, tests, runs, ws, models, settings as settings_api, connectors, prd

app = FastAPI(title="Hendrickson", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(contexts.router, prefix="/api/contexts", tags=["contexts"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
app.include_router(ws.router, prefix="/ws", tags=["websocket"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["connectors"])
app.include_router(prd.router, prefix="/api/prd", tags=["prd"])


@app.on_event("startup")
async def startup():
    app.state.mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    app.state.mongo_db = app.state.mongo_client[settings.mongodb_db]
    app.state.qdrant_client = QdrantClient(
        url=settings.qdrant_url, api_key=settings.qdrant_api_key or None
    )

    app.state.llm = LLMProvider(
        openai_api_key=settings.openai_api_key,
        anthropic_api_key=settings.anthropic_api_key,
        deepseek_api_key=settings.deepseek_api_key,
        openrouter_api_key=settings.openrouter_api_key,
        gemini_api_key=settings.gemini_api_key,
        vertex_project=settings.vertex_project,
        vertex_location=settings.vertex_location,
        ollama_base_url=settings.ollama_base_url,
        default_model=settings.default_llm_model,
    )
    app.state.orchestrator = TestOrchestrator(app.state.llm)
    app.state.vector_store = VectorStore(
        client=app.state.qdrant_client,
        openai_api_key=settings.openai_api_key,
        embedding_model=settings.embedding_model,
    )


@app.on_event("shutdown")
async def shutdown():
    app.state.mongo_client.close()
    app.state.qdrant_client.close()


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
