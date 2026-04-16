from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from o5_council.config import APP_NAME, APP_VERSION
from o5_council.ui.main_window import MainWindow
from o5_council.ui.theme import build_stylesheet


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(build_stylesheet())

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
