from __future__ import annotations

import logging

from twilio.rest import Client

from .config import Config

logger = logging.getLogger(__name__)


class SmsNotifier:
    def __init__(self, config: Config) -> None:
        self._client = Client(config.twilio_account_sid, config.twilio_auth_token)
        self._from_number = config.twilio_from_number
        self._to_number = config.twilio_to_number

    def send(self, message: str) -> None:
        logger.info("Sending SMS: %s", message)
        self._client.messages.create(
            body=message,
            from_=self._from_number,
            to=self._to_number,
        )
