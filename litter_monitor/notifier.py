from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import Config

logger = logging.getLogger(__name__)


class SmsNotifier:
    """Sends texts via an email-to-SMS gateway (e.g. 5551234567@vtext.com).

    Your carrier turns an email sent to that address into a text message on
    your phone, so this just needs a normal SMTP account to send from.
    """

    def __init__(self, config: Config) -> None:
        self._host = config.smtp_host
        self._port = config.smtp_port
        self._username = config.smtp_username
        self._password = config.smtp_password
        self._to_address = config.sms_gateway_address

    def send(self, message: str) -> None:
        logger.info("Sending SMS via %s: %s", self._to_address, message)

        email = EmailMessage()
        email["From"] = self._username
        email["To"] = self._to_address
        email["Subject"] = ""
        email.set_content(message)

        context = ssl.create_default_context()
        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls(context=context)
            server.login(self._username, self._password)
            server.send_message(email)
