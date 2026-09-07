"""Batch orchestration and output persistence."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.case_summary import generate_case_summary
from src.config import Settings
from src.document_reader import read_documents
from src.email_sender import send_customer_email
from src.extraction import extract_case
from src.llm_client import LLMClient
from src.response_generator import generate_customer_email


LOGGER = logging.getLogger(__name__)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def process_batch(settings: Settings, llm_client: LLMClient) -> Path:
    """Process every readable document and return the final report path."""
    structured_dir = settings.output_dir / "structured_data"
    emails_dir = settings.output_dir / "customer_emails"
    summaries_dir = settings.output_dir / "case_summaries"
    for directory in (structured_dir, emails_dir, summaries_dir):
        directory.mkdir(parents=True, exist_ok=True)

    documents, read_errors = read_documents(settings.data_dir)
    rows: List[Dict[str, Any]] = [
        {"source_file": "<batch>", "processing_error": error}
        for error in read_errors
    ]

    for document in documents:
        row: Dict[str, Any] = {
            "source_file": document.source_path.name,
            "extraction_status": "not_started",
            "email_generation_status": "not_started",
            "summary_status": "not_started",
            "sender_email": settings.sender_email or "",
            "email_sent": False,
            "processing_error": "",
        }
        try:
            case = extract_case(document.text, llm_client)
            row.update(case.model_dump())
            row["extraction_status"] = "completed"

            email = generate_customer_email(case, llm_client)
            row["email_generation_status"] = "completed"

            summary = generate_case_summary(case, llm_client)
            row["summary_status"] = "completed"

            stem = document.source_path.stem
            (structured_dir / f"{stem}.json").write_text(
                json.dumps(case.model_dump(), indent=2), encoding="utf-8"
            )
            _write_text(
                emails_dir / f"{stem}.txt",
                f"From: {settings.sender_email or '[SENDER_EMAIL not configured]'}\n"
                f"To: {case.email or '[customer email not found]'}\n"
                f"Subject: {email.subject}\n\n{email.body}\n",
            )
            if settings.send_emails:
                send_customer_email(case.email, email, settings)
                row["email_sent"] = True
            _write_text(
                summaries_dir / f"{stem}.txt",
                "\n".join(
                    [
                        f"Case overview: {summary.case_overview}",
                        f"Key issue: {summary.key_issue}",
                        f"Action taken: {summary.action_taken}",
                        f"Current status: {summary.current_status}",
                        f"Recommended next action: {summary.recommended_next_action}",
                    ]
                )
                + "\n",
            )
        except Exception as exc:
            LOGGER.exception("Failed to process %s", document.source_path.name)
            row["processing_error"] = str(exc)
        rows.append(row)

    report_path = settings.output_dir / "final_report.csv"
    pd.DataFrame(rows).to_csv(report_path, index=False)
    LOGGER.info("Batch complete: %d documents, report at %s", len(documents), report_path)
    return report_path