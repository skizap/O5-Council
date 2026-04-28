from __future__ import annotations

import datetime
import uuid
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from o5_council.config import APP_TITLE, APP_VERSION, COMMON_OPENROUTER_MODELS
from o5_council.history_store import HistoryStore
from o5_council.models import (
    FinalRunResult,
    HistoryRecord,
    MemberResponse,
    RoundSummary,
)
from o5_council.settings_store import SettingsStore
from o5_council.workers import WorkerController


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings_store = SettingsStore()
        self.settings_data = self.settings_store.load()
        self.history_store = HistoryStore()
        self.worker_controller = WorkerController()
        self.current_result: FinalRunResult | None = None
        self.worker = None
        self.active_history_record: HistoryRecord | None = None

        self.name_inputs: list[QLineEdit] = []
        self.role_inputs: list[QLineEdit] = []
        self.model_inputs: list[QComboBox] = []
        self.temperature_inputs: list[QDoubleSpinBox] = []
        self.transcript_views: list[QTextBrowser] = []

        self.setWindowTitle(f"{APP_TITLE} {APP_VERSION}")
        self.resize(1480, 920)
        self._build_ui()
        self._load_settings_into_form()
        self._refresh_history_list()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 10, 12, 10)
        root_layout.setSpacing(8)

        hero = self._build_hero()
        root_layout.addWidget(hero)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        root_layout.addWidget(splitter)

        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready.")

    def _build_hero(self) -> QWidget:
        banner = QWidget()
        banner.setFixedHeight(56)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(8, 0, 8, 0)
        banner_layout.setSpacing(12)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("O5 Council")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #f0f6fc;")

        subtitle = QLabel(
            "Coordinate five OpenRouter models through structured deliberation."
        )
        subtitle.setStyleSheet("font-size: 12px; color: #8b9ab5;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self.summary_label = QLabel(
            "Configure the council, submit a task, and inspect each member before accepting the final synthesis."
        )
        self.summary_label.setWordWrap(True)
        self.summary_label.setMaximumWidth(500)
        self.summary_label.setStyleSheet("font-size: 12px; color: #8b9ab5;")
        self.summary_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        banner_layout.addLayout(title_layout, 1)
        banner_layout.addStretch(1)
        banner_layout.addWidget(self.summary_label, 0)
        return banner

    def _build_left_panel(self) -> QWidget:
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(4, 4, 4, 4)
        inner_layout.setSpacing(10)

        inner_layout.addWidget(self._build_api_box())
        inner_layout.addWidget(self._build_run_settings_box())
        inner_layout.addWidget(self._build_council_box())
        inner_layout.addWidget(self._build_task_box())
        inner_layout.addWidget(self._build_action_box())
        inner_layout.addStretch(1)

        scroll.setWidget(inner)
        outer.addWidget(scroll)
        return container

    def _build_right_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.activity_box = QPlainTextEdit()
        self.activity_box.setReadOnly(True)
        self.activity_box.setPlaceholderText("Council activity will appear here.")

        activity_group = QGroupBox("Live Activity")
        activity_group.setMaximumHeight(180)
        activity_layout = QVBoxLayout(activity_group)
        activity_layout.setContentsMargins(10, 14, 10, 10)
        activity_layout.setSpacing(8)
        activity_layout.addWidget(self.activity_box)

        self.transcript_tabs = QTabWidget()
        for index in range(5):
            transcript = QTextBrowser()
            transcript.setOpenExternalLinks(True)
            transcript.setMarkdown(f"# O5-{index + 1}\n\nAwaiting council output.")
            self.transcript_views.append(transcript)
            self.transcript_tabs.addTab(transcript, f"O5-{index + 1}")

        transcript_group = QGroupBox("Member Transcripts")
        transcript_layout = QVBoxLayout(transcript_group)
        transcript_layout.setContentsMargins(10, 14, 10, 10)
        transcript_layout.setSpacing(8)
        transcript_layout.addWidget(self.transcript_tabs)

        self.final_output = QTextBrowser()
        self.final_output.setOpenExternalLinks(True)
        self.final_output.setMarkdown(
            "# Final Synthesis\n\nThe council has not run yet."
        )

        final_group = QGroupBox("Final Synthesis")
        final_layout = QVBoxLayout(final_group)
        final_layout.setContentsMargins(10, 14, 10, 10)
        final_layout.setSpacing(8)
        final_layout.addWidget(self.final_output)
        self.final_output.setStyleSheet("font-size: 14px;")

        layout.addWidget(activity_group, 1)
        layout.addWidget(transcript_group, 3)
        layout.addWidget(final_group, 2)
        layout.addWidget(self._build_history_panel())
        return container

    def _build_api_box(self) -> QWidget:
        box = QGroupBox("OpenRouter Connection")
        form = QFormLayout(box)
        form.setContentsMargins(10, 14, 10, 10)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(8)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your OpenRouter API key")

        self.site_url_input = QLineEdit()
        self.site_url_input.setPlaceholderText("Optional referer URL")

        self.site_name_input = QLineEdit()
        self.site_name_input.setPlaceholderText("Optional app title")

        form.addRow("API Key", self.api_key_input)
        form.addRow("Site URL", self.site_url_input)
        form.addRow("Site Name", self.site_name_input)
        return box

    def _build_run_settings_box(self) -> QWidget:
        box = QGroupBox("Deliberation Settings")
        form = QFormLayout(box)
        form.setContentsMargins(10, 14, 10, 10)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(8)

        self.task_mode_input = QComboBox()
        self.task_mode_input.setEditable(True)
        self.task_mode_input.addItems(
            [
                "Strategic plan",
                "Policy memo",
                "Research brief",
                "Decision support",
                "Technical proposal",
                "General analysis",
            ]
        )

        self.max_rounds_input = QSpinBox()
        self.max_rounds_input.setRange(1, 8)

        self.consensus_target_input = QSpinBox()
        self.consensus_target_input.setRange(2, 5)

        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(15, 600)
        self.timeout_input.setSuffix(" seconds")

        form.addRow("Task Mode", self.task_mode_input)
        form.addRow("Max Rounds", self.max_rounds_input)
        form.addRow("Consensus Target", self.consensus_target_input)
        form.addRow("Request Timeout", self.timeout_input)
        return box

    def _build_council_box(self) -> QWidget:
        box = QGroupBox("Council Members")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 14, 10, 10)
        layout.setSpacing(8)

        note = QLabel(
            "Each member can use a different OpenRouter model and role prompt. Editable fields let you tune the council without changing code."
        )
        note.setProperty("muted", True)
        note.setWordWrap(True)
        layout.addWidget(note)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        grid.addWidget(QLabel("Name"), 0, 0)
        grid.addWidget(QLabel("Role"), 0, 1)
        grid.addWidget(QLabel("Model"), 0, 2)
        grid.addWidget(QLabel("Temperature"), 0, 3)

        for row in range(5):
            name_input = QLineEdit()
            role_input = QLineEdit()
            model_input = QComboBox()
            model_input.setEditable(True)
            model_input.addItems(COMMON_OPENROUTER_MODELS)
            temp_input = QDoubleSpinBox()
            temp_input.setRange(0.0, 2.0)
            temp_input.setDecimals(2)
            temp_input.setSingleStep(0.05)

            self.name_inputs.append(name_input)
            self.role_inputs.append(role_input)
            self.model_inputs.append(model_input)
            self.temperature_inputs.append(temp_input)

            grid.addWidget(name_input, row + 1, 0)
            grid.addWidget(role_input, row + 1, 1)
            grid.addWidget(model_input, row + 1, 2)
            grid.addWidget(temp_input, row + 1, 3)

        layout.addLayout(grid)
        return box

    def _build_task_box(self) -> QWidget:
        box = QGroupBox("Task Composer")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 14, 10, 10)
        layout.setSpacing(8)

        self.prompt_input = QPlainTextEdit()
        self.prompt_input.setPlaceholderText(
            "Ask the council for a plan, research brief, strategy review, or policy recommendation."
        )
        self.prompt_input.setMinimumHeight(140)

        self.context_input = QPlainTextEdit()
        self.context_input.setPlaceholderText(
            "Optional context, assumptions, constraints, stakeholders, or budget notes."
        )
        self.context_input.setMinimumHeight(100)

        layout.addWidget(QLabel("Primary Task"))
        layout.addWidget(self.prompt_input)
        layout.addWidget(QLabel("Additional Context"))
        layout.addWidget(self.context_input)
        return box

    def _build_action_box(self) -> QWidget:
        box = QGroupBox("Run Controls")
        layout = QHBoxLayout(box)
        layout.setContentsMargins(10, 14, 10, 10)
        layout.setSpacing(8)

        self.start_button = QPushButton("Start Council")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.setProperty("secondary", True)
        self.export_button = QPushButton("Export Markdown")
        self.export_button.setEnabled(False)
        self.export_button.setProperty("secondary", True)
        self.clear_button = QPushButton("Clear Output")
        self.clear_button.setProperty("secondary", True)

        self.start_button.clicked.connect(self.start_run)
        self.cancel_button.clicked.connect(self.cancel_run)
        self.export_button.clicked.connect(self.export_markdown)
        self.clear_button.clicked.connect(self.clear_outputs)

        layout.addWidget(self.start_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.export_button)
        layout.addWidget(self.clear_button)
        return box

    def _load_settings_into_form(self) -> None:
        data = self.settings_data
        self.api_key_input.setText(data.get("api_key", ""))
        self.site_url_input.setText(data.get("site_url", ""))
        self.site_name_input.setText(data.get("site_name", ""))
        self.task_mode_input.setCurrentText(data.get("task_mode", "Strategic plan"))
        self.max_rounds_input.setValue(int(data.get("max_rounds", 3)))
        self.consensus_target_input.setValue(int(data.get("consensus_target", 3)))
        self.timeout_input.setValue(int(data.get("request_timeout", 120)))

        council = data.get("council", [])
        for index in range(min(5, len(council))):
            member = council[index]
            self.name_inputs[index].setText(member.get("name", f"O5-{index + 1}"))
            self.role_inputs[index].setText(member.get("role", "Council Member"))
            self.model_inputs[index].setCurrentText(
                member.get("model", "openai/gpt-4.1-mini")
            )
            self.temperature_inputs[index].setValue(
                float(member.get("temperature", 0.7))
            )
            self.transcript_tabs.setTabText(
                index, member.get("name", f"O5-{index + 1}")
            )

    def _collect_settings(self) -> dict[str, Any]:
        council = []
        for index in range(5):
            council.append(
                {
                    "name": self.name_inputs[index].text().strip() or f"O5-{index + 1}",
                    "role": self.role_inputs[index].text().strip() or "Council Member",
                    "model": self.model_inputs[index].currentText().strip(),
                    "temperature": self.temperature_inputs[index].value(),
                }
            )
        return {
            "api_key": self.api_key_input.text().strip(),
            "site_url": self.site_url_input.text().strip(),
            "site_name": self.site_name_input.text().strip(),
            "task_mode": self.task_mode_input.currentText().strip(),
            "max_rounds": self.max_rounds_input.value(),
            "consensus_target": self.consensus_target_input.value(),
            "request_timeout": self.timeout_input.value(),
            "council": council,
        }

    def start_run(self) -> None:
        settings = self._collect_settings()
        prompt = self.prompt_input.toPlainText().strip()
        context = self.context_input.toPlainText().strip()

        if not settings["api_key"]:
            QMessageBox.warning(
                self,
                "Missing API Key",
                "Please provide your OpenRouter API key before starting the council.",
            )
            return
        if not prompt:
            QMessageBox.warning(
                self, "Missing Task", "Please enter a task for the council."
            )
            return

        self.settings_store.save(settings)
        self.current_result = None
        self.active_history_record = None
        self.export_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.start_button.setObjectName("startButton")
        self.start_button.setProperty("running", True)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        self.cancel_button.setEnabled(True)
        self.clear_outputs()

        for index, member in enumerate(settings["council"]):
            self.transcript_tabs.setTabText(index, member["name"])

        run_config = {
            **settings,
            "prompt": prompt,
            "context": context,
        }
        self.worker = self.worker_controller.start(run_config)
        self.worker.status.connect(self.on_status)
        self.worker.member_update.connect(self.on_member_update)
        self.worker.round_update.connect(self.on_round_update)
        self.worker.completed.connect(self.on_completed)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.on_worker_finished)

        self.summary_label.setText(
            "The council is in session. Watch each member revise its position as consensus develops."
        )
        self.statusBar().showMessage("Council run started.")
        self._append_log("Council run started.")

    def cancel_run(self) -> None:
        self.worker_controller.cancel()
        self._append_log(
            "Cancellation requested. The run will stop after the current request returns."
        )
        self.statusBar().showMessage("Cancellation requested.")

    def clear_outputs(self) -> None:
        self.activity_box.clear()
        for index, transcript in enumerate(self.transcript_views):
            transcript.setMarkdown(
                f"# {self.transcript_tabs.tabText(index)}\n\nAwaiting council output."
            )
        self.final_output.setMarkdown(
            "# Final Synthesis\n\nThe council has not run yet."
        )

    def export_markdown(self) -> None:
        if self.active_history_record is not None:
            text = self.active_history_record.final_markdown
        elif self.current_result is not None:
            text = self.current_result.final_markdown
        else:
            return

        default_name = "o5-council-report.md"
        path_str, _ = QFileDialog.getSaveFileName(self, "Export Markdown", default_name, "Markdown Files (*.md)")
        if not path_str:
            return

        path = Path(path_str)
        path.write_text(text, encoding="utf-8")
        self.statusBar().showMessage(f"Exported report to {path}.")
        self._append_log(f"Exported final markdown to {path}.")

    def on_status(self, message: str) -> None:
        self._append_log(message)
        self.statusBar().showMessage(message)

    def on_member_update(self, payload: dict[str, Any]) -> None:
        response: MemberResponse = payload["response"]
        index = self._member_index(response.agent_name)
        reasoning_section = (
            f"## Reasoning / Thinking\n\n{response.reasoning}\n\n"
            if response.reasoning
            else ""
        )
        summary = (
            f"# {response.agent_name}\n\n"
            f"**Role:** {response.role}  \n"
            f"**Model:** {response.model}  \n"
            f"**Round:** {response.round_number}  \n"
            f"**Preferred Option:** {response.signal.preferred_option}  \n"
            f"**Confidence:** {response.signal.confidence}  \n"
            f"**Consensus Ready:** {response.signal.consensus_ready}\n\n"
            f"{reasoning_section}"
            f"## Response\n\n{response.content}\n\n"
            f"## Key Risks\n\n"
            + (
                "\n".join(f"- {risk}" for risk in response.signal.key_risks)
                or "- No risks were explicitly listed."
            )
        )
        self.transcript_views[index].setMarkdown(summary)
        self._append_log(
            f"Received round {response.round_number} update from {response.agent_name} with option '{response.signal.preferred_option}'."
        )

    def on_round_update(self, payload: dict[str, Any]) -> None:
        summary: RoundSummary = payload["summary"]
        self._append_log(
            "Round {round_number} complete. Majority option: {majority}. Majority count: {majority_count}. Ready count: {ready_count}.".format(
                round_number=summary.round_number,
                majority=summary.majority_option,
                majority_count=summary.majority_count,
                ready_count=summary.ready_count,
            )
        )
        if summary.consensus_reached:
            self._append_log("Consensus threshold reached. Preparing final synthesis.")

    def on_completed(self, payload: dict[str, Any]) -> None:
        result: FinalRunResult = payload["result"]
        self.current_result = result
        self.active_history_record = None
        self.final_output.setMarkdown(result.final_markdown)
        self.export_button.setEnabled(True)
        consensus_text = "reached" if result.consensus_reached else "not reached"
        self.summary_label.setText(
            f"The council run is complete. Consensus was {consensus_text}, and the final majority option was '{result.final_majority_option}'."
        )
        self._append_log(f"Final synthesis completed by {result.synthesized_by}.")
        self.statusBar().showMessage("Council run completed.")
        record = HistoryRecord(
            run_id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now().isoformat(),
            task_mode=result.task_mode,
            prompt_excerpt=result.prompt[:120],
            consensus_reached=result.consensus_reached,
            final_majority_option=result.final_majority_option,
            synthesized_by=result.synthesized_by,
            final_markdown=result.final_markdown,
        )
        success = self.history_store.append(record)
        self._refresh_history_list()
        if not success:
            self._append_log("Warning: failed to save run to history.")

    def on_failed(self, message: str) -> None:
        self._append_log(message)
        self.summary_label.setText(
            "The council run ended early. Review the activity log, adjust the settings, and try again."
        )
        self.statusBar().showMessage("Council run failed.")
        QMessageBox.warning(self, "Council Run", message)

    def on_worker_finished(self) -> None:
        self.start_button.setEnabled(True)
        self.start_button.setProperty("running", False)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        self.cancel_button.setEnabled(False)
        self.worker = None

    def _append_log(self, message: str) -> None:
        self.activity_box.appendPlainText(message)

    def _build_history_panel(self) -> QWidget:
        box = QGroupBox("Run History")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 14, 10, 10)
        layout.setSpacing(8)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(120)

        button_layout = QHBoxLayout()
        load_btn = QPushButton("Load Selected")
        clear_btn = QPushButton("Clear History")
        load_btn.clicked.connect(self._load_history_entry)
        clear_btn.clicked.connect(self._clear_history)

        button_layout.addWidget(load_btn)
        button_layout.addWidget(clear_btn)

        layout.addWidget(self.history_list)
        layout.addLayout(button_layout)
        return box

    def _refresh_history_list(self) -> None:
        self.history_list.clear()
        records = self.history_store.load_all()
        for record in reversed(records):
            item = QListWidgetItem()
            consensus = "✓" if record.consensus_reached else "✗"
            text = f"{record.timestamp[:19]} [{record.task_mode}] {consensus} {record.prompt_excerpt}"
            item.setText(text)
            item.setData(Qt.UserRole, record.run_id)
            self.history_list.addItem(item)

    def _load_history_entry(self) -> None:
        current = self.history_list.currentItem()
        if not current:
            return
        run_id = current.data(Qt.UserRole)
        records = self.history_store.load_all()
        for record in records:
            if record.run_id == run_id:
                self.active_history_record = record
                self.final_output.setMarkdown(record.final_markdown)
                self.export_button.setEnabled(True)
                self.summary_label.setText(f"Viewing historical run from {record.timestamp}. Start a new council to overwrite.")
                break

    def _clear_history(self) -> None:
        reply = QMessageBox.question(self, "Clear History", "Remove all run history?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success = self.history_store.clear()
            self._refresh_history_list()
            if success:
                self._append_log("Run history cleared.")
            else:
                self._append_log("Warning: failed to clear run history.")

    def _member_index(self, agent_name: str) -> int:
        for index in range(self.transcript_tabs.count()):
            if self.transcript_tabs.tabText(index) == agent_name:
                return index
        return 0
