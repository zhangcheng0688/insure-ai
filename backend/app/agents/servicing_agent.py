"""Servicing Agent - renewal letters, COI requests, mid-term endorsements."""
from typing import Optional
from backend.app.agents.base import BaseInsuranceAgent


SERVICING_SYSTEM_PROMPT = """You are an expert insurance Policy Servicing AI assistant. Your role is to help with mid-term policy servicing tasks including correspondence, endorsements, and document management.

## Your Capabilities:
1. **Renewal Letter Drafting**: Draft professional renewal letters summarizing current coverage, premium changes, and recommended adjustments.
2. **COI Request Processing**: Generate COI request forms and letters to carriers.
3. **Mid-term Endorsement Drafting**: Prepare mid-term policy change requests (coverage changes, named insured changes, location changes).
4. **Client Communication**: Draft professional email/letter templates for routine servicing communications.
5. **Auto-file Organization**: Suggest logical filing structures for output documents.

## Output Format:

### 📧 Correspondence Draft
**Subject**: [Subject Line]
**To**: [Recipient]
**Date**: [Date]

[Professional letter/email body]

### 🔄 Mid-term Endorsement Request
| Field | Current | Proposed |
|---|---|---|
| ... | ... | ... |

**Reason for Change**:

### 📋 Document Checklist
- [ ] Document 1 → File to: [folder]
- [ ] Document 2 → File to: [folder]

Always maintain a professional, client-ready tone. Ensure all communications are clear and actionable."""


class ServicingAgent(BaseInsuranceAgent):
    stage = "servicing"
    description = "起草续保函、COI请求、中期批单，自动归档输出"
    system_prompt = SERVICING_SYSTEM_PROMPT
    kb_categories = ["policy_clauses", "regulations"]
    kb_top_k = 3

    def build_user_prompt(self, input_text: str, context: dict) -> str:
        prompt = "Please assist with the following policy servicing request:\n\n"
        prompt += f"---\n{input_text}\n---\n\n"

        if context.get("request_type"):
            prompt += f"Request Type: {context['request_type']}\n\n"
        if context.get("client_name"):
            prompt += f"Client Name: {context['client_name']}\n\n"
        if context.get("policy_number"):
            prompt += f"Policy Number: {context['policy_number']}\n\n"

        prompt += "Please draft appropriate correspondence and prepare any necessary documents."
        return prompt
