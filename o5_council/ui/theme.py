from __future__ import annotations


def build_stylesheet() -> str:
    return """
    QWidget {
        background-color: #0d1117;
        color: #f0f6fc;
        font-family: "Inter", "Segoe UI", Arial, sans-serif;
        font-size: 13px;
    }
    QLabel {
        line-height: 1.4;
        font-size: 13px;
    }
    QTabWidget::pane, QTextEdit, QPlainTextEdit, QListWidget, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
        background-color: #1c2333;
        border: 1px solid #2d3a52;
        border-radius: 10px;
    }
    QFrame {
        background-color: #161b27;
        border: 1px solid #2d3a52;
        border-radius: 10px;
    }
    QTextEdit, QPlainTextEdit, QListWidget {
        padding: 8px;
    }
    QGroupBox {
        background-color: #161b27;
        border: 1px solid #2d3a52;
        border-radius: 12px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: 600;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 4px;
        color: #60a5fa;
    }
    QPushButton {
        background-color: #3b82f6;
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 600;
        letter-spacing: 0.3px;
        color: #ffffff;
    }
    QPushButton:hover {
        background-color: #60a5fa;
        border-color: #60a5fa;
    }
    QPushButton:pressed {
        background-color: #2563eb;
        border-color: #2563eb;
    }
    QPushButton:disabled {
        background-color: #1c2333;
        color: #8b9ab5;
        border-color: #2d3a52;
    }
    QPushButton[secondary="true"] {
        background-color: transparent;
        border: 1px solid #2d3a52;
        color: #8b9ab5;
    }
    QPushButton[secondary="true"]:hover {
        border-color: #3b82f6;
        color: #f0f6fc;
    }
    QPushButton#startButton[running="true"] {
        background-color: #1e3a5f;
        border: 1px solid #3b82f6;
        color: #93c5fd;
    }
    QLabel[muted="true"] {
        color: #8b9ab5;
        font-size: 12px;
        line-height: 1.5;
    }
    QTabBar::tab {
        background: #161b27;
        color: #8b9ab5;
        border: 1px solid #2d3a52;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 9px 18px;
        margin-right: 4px;
    }
    QTabBar::tab:hover {
        background: #1c2333;
        color: #f0f6fc;
    }
    QTabBar::tab:selected {
        background: #1c2333;
        color: #f0f6fc;
        border-bottom: 2px solid #3b82f6;
    }
    QScrollBar:vertical {
        background: #0d1117;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #2d3a52;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #3b82f6;
    }
    QScrollBar::add-line:vertical {
        height: 0;
    }
    QScrollBar::sub-line:vertical {
        height: 0;
    }
    QSplitter::handle {
        background: #2d3a52;
        width: 2px;
        margin: 4px 0;
    }
    QStatusBar {
        background-color: #0d1117;
        color: #8b9ab5;
        font-size: 12px;
        border-top: 1px solid #2d3a52;
    }
    """
