"""Celery task queue for async processing."""
from celery import Celery
from backend.app.core.config import settings

celery_app = Celery(
    "insureai",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="process_document_async")
def process_document_async(stage: str, file_path: str, context: dict, provider: str, model: str):
    """Async task to process an insurance document through an AI agent."""
    from backend.app.agents.registry import get_agent
    from backend.app.utils.pdf_utils import extract_text
    from backend.app.utils.template_engine import render_markdown_to_pdf
    import os

    try:
        input_text = extract_text(file_path)
        agent = get_agent(stage, provider=provider or None, model=model or None)
        result = agent.process(input_text, context)  # Note: sync version for Celery

        pdf_path = None
        if result.success and result.output_markdown:
            import uuid
            pdf_name = f"{stage}_{uuid.uuid4().hex[:8]}.pdf"
            pdf_path = render_markdown_to_pdf(
                result.output_markdown,
                os.path.join(settings.output_dir, pdf_name),
                f"{stage.title()} Document",
            )

        return {
            "success": result.success,
            "markdown": result.output_markdown,
            "pdf_path": pdf_path,
            "error": result.error,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
