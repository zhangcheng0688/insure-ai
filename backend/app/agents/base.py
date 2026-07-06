"""Agent base class for insurance AI agents — with RAG knowledge base integration."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from backend.app.core.llm import llm_chat, build_prompt


@dataclass
class AgentResult:
    """Standardized agent output."""
    success: bool
    stage: str
    output_markdown: str = ""
    output_pdf_path: Optional[str] = None
    output_docx_path: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    knowledge_sources: list[dict] = field(default_factory=list)  # 引用的知识库来源
    error: Optional[str] = None


class BaseInsuranceAgent(ABC):
    """Base class for all insurance-stage AI agents — now with RAG support."""

    stage: str = "base"
    description: str = ""

    # Override in subclass
    system_prompt: str = ""

    # Knowledge base categories to search (override in subclass)
    kb_categories: list[str] = ["policy_clauses"]

    # Number of knowledge chunks to retrieve
    kb_top_k: int = 5

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider
        self.model = model

    @abstractmethod
    def build_user_prompt(self, input_text: str, context: dict) -> str:
        """Build the user prompt from input text and additional context."""
        ...

    def build_search_query(self, input_text: str, context: dict) -> str:
        """Build a search query for the knowledge base. Override for stage-specific queries."""
        # Default: use first 300 chars of input as search query
        return input_text[:300]

    def post_process(self, output: str) -> str:
        """Optional post-processing hook."""
        return output

    def _get_knowledge_context(self, input_text: str, context: dict) -> tuple[str, list[dict]]:
        """Retrieve relevant knowledge from the knowledge base.
        Returns (formatted_context_string, list_of_source_dicts).
        """
        try:
            from backend.app.services.knowledge_base import get_knowledge_base
            kb = get_knowledge_base()

            query = self.build_search_query(input_text, context)
            result = kb.search(
                query=query,
                top_k=self.kb_top_k,
                category=None,  # search all categories
            )

            if not result.chunks:
                return "", []

            context_str = kb.format_for_prompt(result)
            sources = [
                {
                    "content": c.content[:200],
                    "source": c.source,
                    "category": c.category,
                    "score": c.relevance_score,
                }
                for c in result.chunks
            ]
            return context_str, sources
        except Exception:
            # Graceful degradation: if KB is unavailable, continue without it
            return "", []

    async def process(self, input_text: str, context: Optional[dict] = None) -> AgentResult:
        """Run the agent: KB检索 → Prompt构建 → LLM → 后处理."""
        context = context or {}
        try:
            # Step 1: Retrieve knowledge from KB
            kb_context, kb_sources = self._get_knowledge_context(input_text, context)

            # Step 2: Build prompts with knowledge injected
            user_prompt = self.build_user_prompt(input_text, context)

            # Inject knowledge into system prompt if available
            enhanced_system = self.system_prompt
            if kb_context:
                enhanced_system += (
                    "\n\n---\n\n"
                    "## 📚 重要：以下是知识库中检索到的真实保险知识，"
                    "请在分析时优先参考这些内容，并注明引用来源。\n\n"
                    + kb_context
                )

            messages = build_prompt(enhanced_system, user_prompt)

            # Step 3: LLM call
            llm_output = await llm_chat(
                messages,
                provider=self.provider,
                model=self.model,
                temperature=0.3,
                max_tokens=4096,
            )

            # Step 4: Post-process
            processed = self.post_process(llm_output)

            return AgentResult(
                success=True,
                stage=self.stage,
                output_markdown=processed,
                knowledge_sources=kb_sources,
                metadata={
                    "provider": self.provider,
                    "model": self.model,
                    "kb_chunks_used": len(kb_sources),
                },
            )
        except Exception as e:
            return AgentResult(
                success=False,
                stage=self.stage,
                error=str(e),
            )

    def get_info(self) -> dict:
        """Return agent metadata for the UI."""
        return {
            "stage": self.stage,
            "description": self.description,
            "kb_categories": self.kb_categories,
        }
