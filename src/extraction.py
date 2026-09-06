"""Structured complaint extraction stage."""

import json

from src.llm_client import LLMClient
from src.models import ExtractedCase


EXTRACTION_SYSTEM_PROMPT = """You extract customer complaint information from source documents.
Return only a JSON object matching the requested schema. Use null when a text field
is not present. Never infer or invent customer details. Boolean values must be true
only when supported by the source document.
"""


def extract_case(raw_text: str, llm_client: LLMClient) -> ExtractedCase:
    """Extract and validate one complaint document with the LLM."""
    user_prompt = f"""Extract this document into the following fields:
customer_name, email, phone, complaint_category, issue_description,
resolution_provided, is_complaint, escalation_required,
supporting_document_available, case_status.

Source document:
{raw_text}
"""
    payload = llm_client.generate_json(EXTRACTION_SYSTEM_PROMPT, user_prompt)
    return ExtractedCase.model_validate(json.loads(json.dumps(payload)))