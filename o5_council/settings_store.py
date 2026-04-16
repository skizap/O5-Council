from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Any

from o5_council.config import (
    DEFAULT_CONSENSUS_TARGET,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_MODELS,
    DEFAULT_ROLE_SET,
    DEFAULT_TASK_MODE,
    get_settings_path,
)
from o5_council.models import AgentConfig


def build_default_settings() -> dict[str, Any]:
    council = [
        asdict(AgentConfig(name=f"O5-{index + 1}", role=role, model=model))
        for index, (role, model) in enumerate(zip(DEFAULT_ROLE_SET, DEFAULT_MODELS, strict=True))
    ]
    return {
        "api_key": "",
        "task_mode": DEFAULT_TASK_MODE,
        "max_rounds": DEFAULT_MAX_ROUNDS,
        "consensus_target": DEFAULT_CONSENSUS_TARGET,
        "request_timeout": 120,
        "site_url": "https://github.com/skizap/O5-Council",
        "site_name": "O5 Council",
        "council": council,
    }


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or get_settings_path()

    def load(self) -> dict[str, Any]:
        defaults = build_default_settings()
        if not self.path.exists():
            return defaults

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return defaults

        merged = deepcopy(defaults)
        merged.update({key: value for key, value in data.items() if key != "council"})
        if isinstance(data.get("council"), list) and len(data["council"]) == 5:
            merged["council"] = data["council"]
        return merged

    def save(self, settings: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
