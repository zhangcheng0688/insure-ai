"""Intake Builder API - structured information collection pages."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

# In-memory store for intake forms (MVP)
_intake_forms: dict[str, dict] = {}


class IntakeFormCreate(BaseModel):
    title: str
    description: str = ""
    fields: list[dict]  # [{name, label, type: text/number/select/date, required, options: []}]
    insurance_stage: str = "claims"  # which stage this intake form is for


@router.post("/forms")
async def create_intake_form(form: IntakeFormCreate):
    """Create a new structured intake form."""
    form_id = uuid.uuid4().hex[:8]
    _intake_forms[form_id] = {
        "id": form_id,
        "title": form.title,
        "description": form.description,
        "fields": form.fields,
        "insurance_stage": form.insurance_stage,
        "submissions": [],
    }
    return {"form_id": form_id, "share_url": f"/intake/forms/{form_id}"}


@router.get("/forms")
async def list_intake_forms():
    """List all created intake forms."""
    return {"forms": list(_intake_forms.values())}


@router.get("/forms/{form_id}")
async def get_intake_form(form_id: str):
    """Get a specific intake form by ID."""
    form = _intake_forms.get(form_id)
    if not form:
        return {"error": "Form not found"}
    return form


@router.post("/forms/{form_id}/submit")
async def submit_intake_form(form_id: str, data: dict):
    """Submit data to an intake form."""
    form = _intake_forms.get(form_id)
    if not form:
        return {"error": "Form not found"}
    submission = {"id": uuid.uuid4().hex[:8], "data": data}
    form["submissions"].append(submission)
    return {"status": "submitted", "submission_id": submission["id"]}


@router.get("/stages")
async def get_intake_stages():
    """List available stages for intake forms."""
    return {
        "stages": [
            {"key": "claims", "label": "⚠️ 理赔受理"},
            {"key": "new_business", "label": "📋 新业务提交"},
            {"key": "underwriting", "label": "🔍 核保信息收集"},
            {"key": "renewal", "label": "📈 续保问卷"},
            {"key": "servicing", "label": "🔄 服务请求"},
        ]
    }
