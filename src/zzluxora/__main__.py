"""main.py — aplikasi entry point (tanpa splash — D7 user decision).

ZZLUXORA v9. Jalankan: python -m zzluxora.app
"""
from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from zzluxora.app import AppContext
from zzluxora.logging_conf import get_logger, setup_logging
from zzluxora.ui.main_window import MainWindow
from zzluxora.ui.styles import FONT_UI, build_qss

log = get_logger("main")


def main() -> int:
    setup_logging()
    log.info("ZZLUXORA v9 starting...")

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("ZZLUXORA")
    app.setOrganizationName("UNNES")
    app.setApplicationVersion("9.0.0")
    app.setFont(QFont(FONT_UI, 10))
    app.setStyleSheet(build_qss())

    ctx = AppContext()
    window = MainWindow(ctx)
    window.show()

    log.info("Main window shown — ready.")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
