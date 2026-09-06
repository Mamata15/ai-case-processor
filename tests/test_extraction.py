from typing import Any, Dict

from src.extraction import extract_case


class FakeLLMClient:
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        assert "Never infer or invent" in system_prompt
        assert "Refund not received" in user_prompt
        return {
            "customer_name": "Asha Rao",
            "email": "asha@example.com",
            "phone": None,
            "complaint_category": "Billing",
            "issue_description": "Refund not received",
            "resolution_provided": None,
            "is_complaint": True,
            "escalation_required": False,
            "supporting_document_available": False,
            "case_status": "Open",
        }


def test_extract_case_returns_pydantic_model() -> None:
    case = extract_case("Refund not received", FakeLLMClient())

    assert case.customer_name == "Asha Rao"
    assert case.is_complaint is True
    assert case.case_status == "Open"