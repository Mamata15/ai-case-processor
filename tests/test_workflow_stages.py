from typing import Any, Dict

from src.case_summary import generate_case_summary
from src.models import ExtractedCase
from src.response_generator import generate_customer_email


class FakeLLMClient:
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if "customer service email" in system_prompt:
            return {"subject": "Complaint received", "body": "We received your complaint."}
        return {
            "case_overview": "Customer reported a billing issue.",
            "key_issue": "Refund not received.",
            "action_taken": "Complaint recorded.",
            "current_status": "Open",
            "recommended_next_action": "Review the refund status.",
        }


def test_downstream_stages_use_structured_case() -> None:
    case = ExtractedCase(issue_description="Refund not received", case_status="Open")
    client = FakeLLMClient()

    email = generate_customer_email(case, client)
    summary = generate_case_summary(case, client)

    assert email.subject == "Complaint received"
    assert summary.current_status == "Open"