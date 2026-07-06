"""Settings API - LLM configuration and provider listing."""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.llm import get_available_providers
from backend.app.core.config import settings

router = APIRouter()


@router.get("/providers")
async def list_providers():
    """List all available LLM providers and their models."""
    return {
        "providers": get_available_providers(),
        "default_provider": settings.default_llm_provider,
        "default_model": settings.default_llm_model,
    }


class LLMConfigUpdate(BaseModel):
    provider: str
    model: str


@router.post("/update")
async def update_llm_config(config: LLMConfigUpdate):
    """Update the default LLM provider and model (runtime only)."""
    # In a real app, this would persist. For MVP, we use in-memory.
    settings.default_llm_provider = config.provider
    settings.default_llm_model = config.model
    return {
        "status": "ok",
        "default_provider": config.provider,
        "default_model": config.model,
    }
