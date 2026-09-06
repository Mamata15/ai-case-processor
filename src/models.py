"""Pydantic models used by the processing workflow."""

from pydantic import BaseModel, Field
from typing import Optional


class ExtractedCase(BaseModel):
    """Structured information extracted from one complaint document."""

    customer_name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    complaint_category: Optional[str] = Field(default=None)
    issue_description: str = Field(default="")
    resolution_provided: Optional[str] = Field(default=None)
    is_complaint: bool = False
    escalation_required: bool = False
    supporting_document_available: bool = False
    case_status: str = Field(default="Unknown")


class CaseSummary(BaseModel):
    """Internal management summary for a processed case."""

    case_overview: str
    key_issue: str
    action_taken: str
    current_status: str
    recommended_next_action: str


class CustomerEmail(BaseModel):
    """Generated customer-facing email."""

    subject: str
    body: str