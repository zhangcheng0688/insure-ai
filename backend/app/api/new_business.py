"""New Business API endpoints."""
from fastapi import APIRouter, UploadFile, File, Form
from backend.app.agents.registry import get_agent
from backend.app.utils.pdf_utils import extract_text
from backend.app.utils.template_engine import render_markdown_to_pdf
from backend.app.core.config import settings
import os, uuid

router = APIRouter()


@router.post("/analyze")
async def analyze_new_business(
    file: UploadFile = File(None),
    text: str = Form(""),
    additional_notes: str = Form(""),
    provider: str = Form(""),
    model: str = Form(""),
):
    """Analyze new business submission: ACORD form + risk extraction + worksheet."""
    input_text = text
    if file and file.filename:
        file_path = os.path.join(settings.upload_dir, f"nb_{uuid.uuid4().hex[:8]}_{file.filename}")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        input_text = extract_text(file_path) or text

    if not input_text.strip():
        return {"error": "No input text or file provided"}

    agent = get_agent("new_business", provider=provider or None, model=model or None)
    context = {"additional_notes": additional_notes} if additional_notes else {}

    result = await agent.process(input_text, context)

    pdf_path = None
    if result.success and result.output_markdown:
        pdf_name = f"submission_analysis_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = render_markdown_to_pdf(result.output_markdown, os.path.join(settings.output_dir, pdf_name), "New Business Submission Analysis")

    return {
        "success": result.success,
        "markdown": result.output_markdown,
        "pdf_path": pdf_path,
        "error": result.error,
    }
