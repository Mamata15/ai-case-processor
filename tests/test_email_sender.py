from email.message import EmailMessage
from pathlib import Path
from typing import Any

from src.config import Settings
from src.email_sender import send_customer_email
from src.models import CustomerEmail


class FakeSMTP:
    sent_message: EmailMessage | None = None

    def __init__(self, host: str, port: int, timeout: int):
        assert host == "smtp.example.com"
        assert port == 587
        assert timeout == 30

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def starttls(self) -> None:
        pass

    def login(self, username: str, password: str) -> None:
        assert username == "user"
        assert password == "password"

    def send_message(self, message: EmailMessage) -> None:
        FakeSMTP.sent_message = message


def test_sends_generated_email(monkeypatch) -> None:
    import src.email_sender as email_sender

    monkeypatch.setattr(email_sender.smtplib, "SMTP", FakeSMTP)
    settings = Settings(
        data_dir=Path("data"),
        output_dir=Path("output"),
        smtp_host="smtp.example.com",
        smtp_username="user",
        smtp_password="password",
        sender_email="support@example.com",
    )

    send_customer_email(
        "customer@example.com",
        CustomerEmail(subject="Complaint received", body="We received your complaint."),
        settings,
    )

    assert FakeSMTP.sent_message["To"] == "customer@example.com"
    assert FakeSMTP.sent_message["Subject"] == "Complaint received"