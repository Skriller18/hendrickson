from fastapi import APIRouter, Request

from src.agents.models import PROVIDERS, get_all_models, ModelInfo

router = APIRouter()


@router.get("/")
async def list_models():
    models = get_all_models()
    return {
        "providers": {
            key: {
                "name": data["name"],
                "models": [m.model_dump() for m in data["models"]],
            }
            for key, data in PROVIDERS.items()
        },
        "all": [m.model_dump() for m in models],
    }


@router.get("/providers")
async def list_providers():
    return {
        key: {"name": data["name"], "model_count": len(data["models"])}
        for key, data in PROVIDERS.items()
    }
