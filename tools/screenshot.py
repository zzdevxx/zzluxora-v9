"""Grab screenshot ZZLUXORA via QWidget.grab() — reliable headless capture.

Usage: python tools/screenshot.py [output.png]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication

from zzluxora.app import AppContext
from zzluxora.ui.main_window import MainWindow
from zzluxora.ui.styles import build_qss


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/screenshot.png")
    app = QApplication([])
    app.setStyleSheet(build_qss())
    ctx = AppContext()
    w = MainWindow(ctx)
    w.resize(1280, 800)
    w.show()
    app.processEvents()
    app.processEvents()
    pm = w.grab()
    out.parent.mkdir(parents=True, exist_ok=True)
    ok = pm.save(str(out))
    print(f"[screenshot] saved={'YES' if ok else 'NO'} -> {out.resolve()}")
    w.close()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
