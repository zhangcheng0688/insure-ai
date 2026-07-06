"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.router import api_router
from backend.app.agents.registry import list_agents

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered insurance document processing platform covering the full policy lifecycle.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/v1/agents")
async def get_agents():
    """List all available insurance AI agents."""
    return {"agents": list_agents()}
