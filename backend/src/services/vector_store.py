from typing import Optional

from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


COLLECTION_REQUIREMENTS = "hendrickson_requirements"
COLLECTION_CODE = "hendrickson_code"
DEFAULT_VECTOR_SIZE = 1536


class VectorStore:
    def __init__(
        self,
        client: QdrantClient,
        openai_api_key: str = "",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.client = client
        self.embedding_model = embedding_model
        self.openai = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self._ensure_collections()

    def _ensure_collections(self):
        collections = [c.name for c in self.client.get_collections().collections]

        if COLLECTION_REQUIREMENTS not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_REQUIREMENTS,
                vectors_config=VectorParams(size=DEFAULT_VECTOR_SIZE, distance=Distance.COSINE),
            )

        if COLLECTION_CODE not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_CODE,
                vectors_config=VectorParams(size=DEFAULT_VECTOR_SIZE, distance=Distance.COSINE),
            )

    async def get_embedding(self, text: str) -> list[float]:
        if not self.openai:
            return [0.0] * DEFAULT_VECTOR_SIZE

        resp = await self.openai.embeddings.create(
            model=self.embedding_model,
            input=text[:8000],
        )
        return resp.data[0].embedding

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not self.openai:
            return [[0.0] * DEFAULT_VECTOR_SIZE for _ in texts]

        resp = await self.openai.embeddings.create(
            model=self.embedding_model,
            input=[t[:8000] for t in texts],
        )
        return [d.embedding for d in resp.data]

    async def index_requirements(self, requirements: list[dict]):
        if not requirements:
            return

        texts = [req.get("description", "") for req in requirements]
        embeddings = await self.get_embeddings(texts)

        points = [
            PointStruct(
                id=i,
                vector=embeddings[i],
                payload={
                    "tag": req.get("tag", ""),
                    "description": req.get("description", ""),
                    "source_document": req.get("source_document", ""),
                    "section": req.get("section", ""),
                },
            )
            for i, req in enumerate(requirements)
            if i < len(embeddings)
        ]

        if points:
            self.client.upsert(collection_name=COLLECTION_REQUIREMENTS, points=points)

    async def index_code_entities(self, entities: list[dict]):
        if not entities:
            return

        texts = [
            f"{ent.get('name', '')} {ent.get('signature', '')} {ent.get('entity_type', '')}"
            for ent in entities
        ]
        embeddings = await self.get_embeddings(texts)

        points = [
            PointStruct(
                id=i,
                vector=embeddings[i],
                payload={
                    "name": ent.get("name", ""),
                    "entity_type": ent.get("entity_type", ""),
                    "file_path": ent.get("file_path", ""),
                    "signature": ent.get("signature", ""),
                },
            )
            for i, ent in enumerate(entities)
            if i < len(embeddings)
        ]

        if points:
            self.client.upsert(collection_name=COLLECTION_CODE, points=points)

    async def search_requirements(self, query: str, limit: int = 10) -> list[dict]:
        query_vector = await self.get_embedding(query)
        results = self.client.search(
            collection_name=COLLECTION_REQUIREMENTS,
            query_vector=query_vector,
            limit=limit,
        )
        return [hit.payload for hit in results]

    async def search_code(self, query: str, limit: int = 10) -> list[dict]:
        query_vector = await self.get_embedding(query)
        results = self.client.search(
            collection_name=COLLECTION_CODE,
            query_vector=query_vector,
            limit=limit,
        )
        return [hit.payload for hit in results]
