"""Multi-model LLM adapter using LiteLLM."""
import json
from typing import Optional, AsyncIterator
from litellm import acompletion, completion
from pydantic import BaseModel

from backend.app.core.config import settings


# Map providers to LiteLLM model prefixes
PROVIDER_MODELS = {
    "openai": {
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
    },
    "deepseek": {
        "deepseek-chat": "deepseek/deepseek-chat",
        "deepseek-reasoner": "deepseek/deepseek-reasoner",
    },
    "qwen": {
        "qwen-max": "dashscope/qwen-max",
        "qwen-plus": "dashscope/qwen-plus",
        "qwen-turbo": "dashscope/qwen-turbo",
        "qwen-long": "dashscope/qwen-long",
    },
    "anthropic": {
        "claude-sonnet-5": "claude-sonnet-5-20250915",
        "claude-opus-4-8": "claude-opus-4-8-20250805",
        "claude-haiku-4-5": "claude-haiku-4-5-20251001",
    },
}


def get_available_providers() -> list[dict]:
    """Return list of available LLM providers and their models."""
    result = []
    for provider, models in PROVIDER_MODELS.items():
        cfg = settings.get_llm_config(provider)
        has_key = bool(cfg.get("api_key"))
        result.append({
            "name": provider,
            "label": provider.capitalize(),
            "models": list(models.keys()),
            "configured": has_key,
        })
    return result


def resolve_model(provider: str, model_name: str) -> str:
    """Resolve provider + model name to LiteLLM model string."""
    models = PROVIDER_MODELS.get(provider, {})
    return models.get(model_name, model_name)


def get_llm_kwargs(provider: str) -> dict:
    """Get LiteLLM kwargs for a given provider."""
    cfg = settings.get_llm_config(provider)
    kwargs = {}
    if cfg.get("api_key"):
        kwargs["api_key"] = cfg["api_key"]
    if cfg.get("api_base"):
        kwargs["api_base"] = cfg["api_base"]
    return kwargs


async def llm_chat(
    messages: list[dict],
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    response_format: Optional[dict] = None,
) -> str:
    """Send a chat request to the configured LLM and return text response."""
    p = provider or settings.default_llm_provider
    m = model or settings.default_llm_model
    litellm_model = resolve_model(p, m)
    kwargs = get_llm_kwargs(p)

    resp = await acompletion(
        model=litellm_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
        **(response_format or {}),
    )
    return resp.choices[0].message.content or ""


def llm_chat_sync(
    messages: list[dict],
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    """Synchronous version of llm_chat."""
    p = provider or settings.default_llm_provider
    m = model or settings.default_llm_model
    litellm_model = resolve_model(p, m)
    kwargs = get_llm_kwargs(p)

    resp = completion(
        model=litellm_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
    return resp.choices[0].message.content or ""


def build_prompt(system: str, user: str) -> list[dict]:
    """Build a standard system + user message list."""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_vision_prompt(system: str, text: str, image_base64: str, mime_type: str = "image/png") -> list[dict]:
    """Build a multimodal prompt with an image."""
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}},
            ],
        },
    ]
