from pathlib import Path
from typing import Any, Dict

import pandas as pd

from src.batch_processor import process_batch
from src.config import Settings


class FakeLLMClient:
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if "extract customer complaint" in system_prompt:
            return {
                "customer_name": "Test Customer",
                "email": "test@example.com",
                "phone": None,
                "complaint_category": "Billing",
                "issue_description": "Unexpected charge",
                "resolution_provided": None,
                "is_complaint": True,
                "escalation_required": False,
                "supporting_document_available": False,
                "case_status": "Open",
            }
        if "customer service email" in system_prompt:
            return {"subject": "Complaint received", "body": "We received your complaint."}
        return {
            "case_overview": "Billing complaint.",
            "key_issue": "Unexpected charge.",
            "action_taken": "Recorded.",
            "current_status": "Open",
            "recommended_next_action": "Investigate.",
        }


def test_batch_writes_expected_outputs(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "output"
    data_dir.mkdir()
    (data_dir / "case.txt").write_text("A complaint", encoding="utf-8")
    settings = Settings(data_dir=data_dir, output_dir=output_dir)

    report_path = process_batch(settings, FakeLLMClient())

    assert (output_dir / "structured_data/case.json").exists()
    assert (output_dir / "customer_emails/case.txt").exists()
    assert (output_dir / "case_summaries/case.txt").exists()
    report = pd.read_csv(report_path)
    assert report.iloc[0]["customer_name"] == "Test Customer"