"""Internal management summary generation stage."""

import json

from src.llm_client import LLMClient
from src.models import CaseSummary, ExtractedCase


SUMMARY_SYSTEM_PROMPT = """Create a concise internal case summary from the structured data.
Use only facts present in the case and do not invent actions or customer details.
If a recommended action is not explicit, state a cautious follow-up based on the
case status. Return only JSON with case_overview, key_issue, action_taken,
current_status, and recommended_next_action fields.
"""


def generate_case_summary(case: ExtractedCase, llm_client: LLMClient) -> CaseSummary:
    """Generate an internal management summary from validated case data."""
    prompt = "Structured case data:\n" + json.dumps(case.model_dump(), indent=2)
    payload = llm_client.generate_json(SUMMARY_SYSTEM_PROMPT, prompt)
    return CaseSummary.model_validate(payload)