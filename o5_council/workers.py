from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, QThread, Signal

from o5_council.council_engine import CouncilEngine, CouncilRunCancelled
from o5_council.models import AgentConfig
from o5_council.openrouter_client import OpenRouterClient, OpenRouterError


class CouncilWorker(QObject):
    status = Signal(str)
    member_update = Signal(dict)
    round_update = Signal(dict)
    completed = Signal(dict)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, run_config: dict[str, Any]) -> None:
        super().__init__()
        self.run_config = run_config
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True

    def run(self) -> None:
        try:
            council = [AgentConfig(**member) for member in self.run_config["council"]]
            client = OpenRouterClient(
                api_key=self.run_config["api_key"],
                site_url=self.run_config.get("site_url"),
                site_name=self.run_config.get("site_name"),
                timeout_seconds=float(self.run_config.get("request_timeout", 120)),
            )
            engine = CouncilEngine(
                client,
                council,
                progress_callback=self._handle_progress,
                cancel_check=lambda: self._cancel_requested,
            )
            result = engine.run(
                task_mode=self.run_config["task_mode"],
                prompt=self.run_config["prompt"],
                context=self.run_config["context"],
                max_rounds=int(self.run_config["max_rounds"]),
                consensus_target=int(self.run_config["consensus_target"]),
            )
            self.completed.emit({"result": result})
        except CouncilRunCancelled as exc:
            self.failed.emit(str(exc))
        except OpenRouterError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:  # pragma: no cover - defensive UI error path
            self.failed.emit(f"Unexpected error: {exc}")
        finally:
            self.finished.emit()

    def _handle_progress(self, event: str, payload: dict[str, Any]) -> None:
        if event == "status":
            self.status.emit(str(payload.get("message", "")))
        elif event == "member_response":
            self.member_update.emit(payload)
        elif event == "round_complete":
            self.round_update.emit(payload)


class WorkerController:
    def __init__(self) -> None:
        self.thread: QThread | None = None
        self.worker: CouncilWorker | None = None

    def start(self, run_config: dict[str, Any]) -> CouncilWorker:
        self.thread = QThread()
        self.worker = CouncilWorker(run_config)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        return self.worker

    def cancel(self) -> None:
        if self.worker is not None:
            self.worker.cancel()
