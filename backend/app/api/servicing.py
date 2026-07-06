"""Servicing API endpoints."""
from fastapi import APIRouter, UploadFile, File, Form
from backend.app.agents.registry import get_agent
from backend.app.utils.pdf_utils import extract_text
from backend.app.utils.template_engine import render_markdown_to_pdf
from backend.app.core.config import settings
import os, uuid

router = APIRouter()


@router.post("/process")
async def process_servicing(
    file: UploadFile = File(None),
    text: str = Form(""),
    request_type: str = Form(""),
    client_name: str = Form(""),
    policy_number: str = Form(""),
    provider: str = Form(""),
    model: str = Form(""),
):
    """Process servicing request: correspondence + mid-term changes."""
    input_text = text
    if file and file.filename:
        file_path = os.path.join(settings.upload_dir, f"svc_{uuid.uuid4().hex[:8]}_{file.filename}")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        input_text = extract_text(file_path) or text

    if not input_text.strip():
        return {"error": "No input text or file provided"}

    agent = get_agent("servicing", provider=provider or None, model=model or None)
    context = {}
    if request_type:
        context["request_type"] = request_type
    if client_name:
        context["client_name"] = client_name
    if policy_number:
        context["policy_number"] = policy_number

    result = await agent.process(input_text, context)

    pdf_path = None
    if result.success and result.output_markdown:
        pdf_name = f"servicing_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = render_markdown_to_pdf(result.output_markdown, os.path.join(settings.output_dir, pdf_name), "Policy Servicing Documents")

    return {
        "success": result.success,
        "markdown": result.output_markdown,
        "pdf_path": pdf_path,
        "error": result.error,
    }
