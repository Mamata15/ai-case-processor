"""Customer email generation stage."""

import json

from src.llm_client import LLMClient
from src.models import CustomerEmail, ExtractedCase


EMAIL_SYSTEM_PROMPT = """Write a professional customer service email from the structured case.
Use only facts present in the case. Do not invent dates, amounts, policies, promises,
contact details, or actions. If information is missing, use neutral wording rather
than guessing. Return only JSON with subject and body fields.
"""


def generate_customer_email(case: ExtractedCase, llm_client: LLMClient) -> CustomerEmail:
    """Generate a customer-facing email from validated structured data."""
    prompt = "Structured case data:\n" + json.dumps(case.model_dump(), indent=2)
    payload = llm_client.generate_json(EMAIL_SYSTEM_PROMPT, prompt)
    return CustomerEmail.model_validate(payload)