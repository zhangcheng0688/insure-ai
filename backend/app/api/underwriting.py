"""Underwriting API endpoints."""
from fastapi import APIRouter, UploadFile, File, Form
from backend.app.agents.registry import get_agent
from backend.app.utils.pdf_utils import extract_text
from backend.app.utils.template_engine import render_markdown_to_pdf
from backend.app.core.config import settings
import os, uuid

router = APIRouter()


@router.post("/analyze")
async def analyze_underwriting(
    file: UploadFile = File(None),
    text: str = Form(""),
    carrier_guidelines: str = Form(""),
    prior_year_premium: str = Form(""),
    provider: str = Form(""),
    model: str = Form(""),
):
    """Analyze underwriting: loss runs + carrier appetite + memo draft."""
    input_text = text
    if file and file.filename:
        file_path = os.path.join(settings.upload_dir, f"uw_{uuid.uuid4().hex[:8]}_{file.filename}")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        input_text = extract_text(file_path) or text

    if not input_text.strip():
        return {"error": "No input text or file provided"}

    agent = get_agent("underwriting", provider=provider or None, model=model or None)
    context = {}
    if carrier_guidelines:
        context["carrier_guidelines"] = carrier_guidelines
    if prior_year_premium:
        context["prior_year_premium"] = prior_year_premium

    result = await agent.process(input_text, context)

    pdf_path = None
    if result.success and result.output_markdown:
        pdf_name = f"underwriting_memo_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = render_markdown_to_pdf(result.output_markdown, os.path.join(settings.output_dir, pdf_name), "Underwriting Memo")

    return {
        "success": result.success,
        "markdown": result.output_markdown,
        "pdf_path": pdf_path,
        "error": result.error,
    }
