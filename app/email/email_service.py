import aiosmtplib

from email.message import EmailMessage

from app.core.config import settings


class EmailService:

    @staticmethod
    async def send_email(

        to: str,

        subject: str,

        body: str

    ):

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

            start_tls=True

        )