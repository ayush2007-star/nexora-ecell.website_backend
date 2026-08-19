import logging
from email.message import EmailMessage

import aiosmtplib

from app.config import settings


logger = logging.getLogger(__name__)


class EmailService:
    """
    Centralized email service.

    Email configuration is optional during local development.
    A missing SMTP configuration will not crash the main
    registration/admin workflow.
    """

    @staticmethod
    def is_configured() -> bool:
        required_values = (
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD,
            settings.EMAIL_FROM,
        )

        return all(
            value not in (None, "")
            for value in required_values
        )

    @staticmethod
    async def send_email(
        to: str,
        subject: str,
        body: str,
    ) -> bool:
        if not EmailService.is_configured():
            logger.warning(
                "SMTP is not configured. Email skipped for %s.",
                to,
            )
            return False

        message = EmailMessage()

        message["From"] = settings.EMAIL_FROM
        message["To"] = to
        message["Subject"] = subject

        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )

        return True