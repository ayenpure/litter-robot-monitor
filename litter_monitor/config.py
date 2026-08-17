from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Config:
    littlerobot_username: str
    litterrobot_password: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sms_gateway_address: str
    poll_interval_minutes: float
    waste_drawer_full_threshold: float
    litter_level_low_threshold: float
    alert_hysteresis: float
    state_path: str


def load_config() -> Config:
    return Config(
        littlerobot_username=_required("LITTERROBOT_USERNAME"),
        litterrobot_password=_required("LITTERROBOT_PASSWORD"),
        smtp_host=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.environ.get("SMTP_PORT", 587)),
        smtp_username=_required("SMTP_USERNAME"),
        smtp_password=_required("SMTP_PASSWORD"),
        sms_gateway_address=_required("SMS_GATEWAY_ADDRESS"),
        poll_interval_minutes=float(os.environ.get("POLL_INTERVAL_MINUTES", 15)),
        waste_drawer_full_threshold=float(os.environ.get("WASTE_DRAWER_FULL_THRESHOLD", 80)),
        litter_level_low_threshold=float(os.environ.get("LITTER_LEVEL_LOW_THRESHOLD", 20)),
        alert_hysteresis=float(os.environ.get("ALERT_HYSTERESIS", 10)),
        state_path=os.environ.get("STATE_PATH", "data/state.json"),
    )
