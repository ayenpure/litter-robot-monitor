from __future__ import annotations

import json
import os
from typing import Any


class AlertState:
    """Tracks which alerts have already fired, so we don't text on every
    poll while a robot sits above/below a threshold. Persisted to disk so
    state survives restarts.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if os.path.exists(self._path):
            with open(self._path) as f:
                return json.load(f)
        return {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

    def is_active(self, robot_id: str, condition: str) -> bool:
        return bool(self._data.get(robot_id, {}).get(condition, False))

    def set_active(self, robot_id: str, condition: str, active: bool) -> None:
        self._data.setdefault(robot_id, {})[condition] = active
