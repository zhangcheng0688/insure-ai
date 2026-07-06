"""Claims API endpoints."""
from fastapi import APIRouter, UploadFile, File, Form
from backend.app.agents.registry import get_agent
from backend.app.utils.pdf_utils import extract_text
from backend.app.utils.template_engine import render_markdown_to_pdf
from backend.app.core.config import settings
import os
import uuid

router = APIRouter()


@router.post("/analyze")
async def analyze_claim(
    file: UploadFile = File(None),
    text: str = Form(""),
    policy_wording: str = Form(""),
    claim_type: str = Form(""),
    provider: str = Form(""),
    model: str = Form(""),
):
    """Analyze a claim: FNOL summary + policy cross-reference + adjudication memo."""
    # Extract text from uploaded file or use direct text
    input_text = text
    if file and file.filename:
        file_path = os.path.join(settings.upload_dir, f"claims_{uuid.uuid4().hex[:8]}_{file.filename}")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        input_text = extract_text(file_path) or text

    if not input_text.strip():
        return {"error": "No input text or file provided"}

    # Build context
    context = {}
    if policy_wording:
        context["policy_wording"] = policy_wording
    if claim_type:
        context["claim_type"] = claim_type

    # Run agent
    agent = get_agent("claims", provider=provider or None, model=model or None)
    result = await agent.process(input_text, context)

    # Generate PDF
    pdf_path = None
    if result.success and result.output_markdown:
        pdf_name = f"claim_adjudication_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = render_markdown_to_pdf(result.output_markdown, os.path.join(settings.output_dir, pdf_name), "Claim Adjudication Memo")

    return {
        "success": result.success,
        "markdown": result.output_markdown,
        "pdf_path": pdf_path,
        "error": result.error,
        "metadata": result.metadata,
    }
