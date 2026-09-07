"""Optional SMTP delivery for generated customer emails."""

import logging
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

from src.config import Settings
from src.models import CustomerEmail


LOGGER = logging.getLogger(__name__)


class EmailConfigurationError(RuntimeError):
    """Raised when email delivery is enabled but SMTP settings are incomplete."""


def validate_email_settings(settings: Settings) -> None:
    """Validate sender and SMTP settings before attempting delivery."""
    if not settings.sender_email:
        raise EmailConfigurationError("SENDER_EMAIL is required when email sending is enabled")
    if not parseaddr(settings.sender_email)[1]:
        raise EmailConfigurationError("SENDER_EMAIL must be a valid email address")
    if not settings.smtp_host:
        raise EmailConfigurationError("SMTP_HOST is required when email sending is enabled")
    if settings.smtp_port <= 0 or settings.smtp_port > 65535:
        raise EmailConfigurationError("SMTP_PORT must be between 1 and 65535")


def send_customer_email(
    recipient: str | None,
    email: CustomerEmail,
    settings: Settings,
) -> None:
    """Send one generated email through the configured SMTP server."""
    if not recipient:
        raise EmailConfigurationError("Cannot send email because the case has no recipient")
    if not parseaddr(recipient)[1]:
        raise EmailConfigurationError("Customer recipient must be a valid email address")
    validate_email_settings(settings)

    message = EmailMessage()
    message["From"] = settings.sender_email
    message["To"] = recipient
    message["Subject"] = email.subject
    message.set_content(email.body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)

    LOGGER.info("Customer email sent to %s", recipient)