"""Main API router - aggregates all endpoint modules."""
from fastapi import APIRouter

from backend.app.api import claims, underwriting, new_business, policy_issuance, servicing, renewal, intake, settings_llm, auth, kb_manage

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(settings_llm.router, prefix="/settings", tags=["Settings"])
api_router.include_router(claims.router, prefix="/claims", tags=["Claims"])
api_router.include_router(underwriting.router, prefix="/underwriting", tags=["Underwriting"])
api_router.include_router(new_business.router, prefix="/new-business", tags=["New Business"])
api_router.include_router(policy_issuance.router, prefix="/policy-issuance", tags=["Policy Issuance"])
api_router.include_router(servicing.router, prefix="/servicing", tags=["Servicing"])
api_router.include_router(renewal.router, prefix="/renewal", tags=["Renewal"])
api_router.include_router(intake.router, prefix="/intake", tags=["Intake"])
api_router.include_router(kb_manage.router, prefix="/kb", tags=["Knowledge Base"])
