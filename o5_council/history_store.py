from __future__ import annotations

import json
from pathlib import Path

from o5_council.config import get_history_path
from o5_council.models import HistoryRecord


class HistoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or get_history_path()

    def append(self, record: HistoryRecord) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(self._record_to_dict(record)) + "\n"
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line)
            return True
        except OSError:
            return False

    def load_all(self) -> list[HistoryRecord]:
        if not self.path.exists():
            return []

        records: list[HistoryRecord] = []
        try:
            content = self.path.read_text(encoding="utf-8")
        except OSError:
            return []

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                data = json.loads(stripped)
                records.append(self._dict_to_record(data))
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

        return records

    def clear(self) -> bool:
        if not self.path.exists():
            return True
        try:
            self.path.unlink()
            return True
        except OSError:
            return False

    @staticmethod
    def _record_to_dict(record: HistoryRecord) -> dict:
        return {
            "run_id": record.run_id,
            "timestamp": record.timestamp,
            "task_mode": record.task_mode,
            "prompt_excerpt": record.prompt_excerpt,
            "consensus_reached": record.consensus_reached,
            "final_majority_option": record.final_majority_option,
            "synthesized_by": record.synthesized_by,
            "final_markdown": record.final_markdown,
        }

    @staticmethod
    def _dict_to_record(data: dict) -> HistoryRecord:
        return HistoryRecord(
            run_id=data["run_id"],
            timestamp=data["timestamp"],
            task_mode=data["task_mode"],
            prompt_excerpt=data["prompt_excerpt"],
            consensus_reached=data["consensus_reached"],
            final_majority_option=data["final_majority_option"],
            synthesized_by=data["synthesized_by"],
            final_markdown=data["final_markdown"],
        )
