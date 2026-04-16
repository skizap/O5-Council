from __future__ import annotations


def build_stylesheet() -> str:
    return """
    QWidget {
        background-color: #0b1020;
        color: #e6eef8;
        font-family: Inter, Segoe UI, Arial, sans-serif;
        font-size: 13px;
    }
    QMainWindow, QFrame, QTabWidget::pane, QTextEdit, QPlainTextEdit, QListWidget, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
        background-color: #11182b;
        border: 1px solid #24324d;
        border-radius: 10px;
    }
    QTextEdit, QPlainTextEdit, QListWidget {
        padding: 8px;
    }
    QGroupBox {
        border: 1px solid #24324d;
        border-radius: 12px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: 600;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 4px;
        color: #9bb3d4;
    }
    QPushButton {
        background-color: #1d4ed8;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #2563eb;
    }
    QPushButton:disabled {
        background-color: #334155;
        color: #94a3b8;
    }
    QLabel[muted="true"] {
        color: #94a3b8;
    }
    QTabBar::tab {
        background: #11182b;
        color: #bfd2ec;
        border: 1px solid #24324d;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 8px 14px;
        margin-right: 4px;
    }
    QTabBar::tab:selected {
        background: #16203a;
        color: #ffffff;
    }
    QScrollBar:vertical {
        background: #0f172a;
        width: 12px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background: #334155;
        border-radius: 6px;
        min-height: 24px;
    }
    QStatusBar {
        background-color: #0f172a;
        color: #cbd5e1;
    }
    """
