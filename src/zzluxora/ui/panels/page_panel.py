"""Page Panel — Virtual Console page (R1 QLC+ VC / R3 §6).

Grid tombol aksi (scene/flash) ala Virtual Console QLC+:
  - ADD BUTTON: tambah aksi (scene) ke page
  - tombol toggle → flash (warna magenta saat aktif, R3)
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.ui.styles import COLORS

GRID_COLS = 5


class PagePanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self._actions: list[QPushButton] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("VIRTUAL CONSOLE"))
        bar.addStretch(1)
        self.btn_add = QPushButton("ADD BUTTON")
        self.btn_add.setObjectName("addBtn")
        self.btn_add.clicked.connect(lambda: self.add_button(f"Scene {self.action_count()+1}"))
        bar.addWidget(self.btn_add)
        lay.addLayout(bar)

        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        lay.addLayout(self.grid, 1)

    # ── API ───────────────────────────────────────────────────────────
    def action_count(self) -> int:
        return len(self._actions)

    def add_button(self, label: str) -> None:
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setFixedHeight(54)
        btn.setStyleSheet(
            f"background-color: {COLORS['bg_elevated']};"
            f" border: 1px solid {COLORS['border']}; color: {COLORS['text_primary']};"
            f" font-size: 9pt;"
        )
        btn.toggled.connect(lambda on, b=btn: self._flash(b, on))
        idx = len(self._actions)
        self.grid.addWidget(btn, idx // GRID_COLS, idx % GRID_COLS)
        self._actions.append(btn)

    def _flash(self, btn: QPushButton, on: bool) -> None:
        """Flash indicator — magenta saat aktif (R3 design token)."""
        if on:
            btn.setStyleSheet(
                f"background-color: {COLORS['magenta']}; color: #000000;"
                f" border: 1px solid {COLORS['magenta']}; font-size: 9pt;"
            )
        else:
            btn.setStyleSheet(
                f"background-color: {COLORS['bg_elevated']};"
                f" border: 1px solid {COLORS['border']}; color: {COLORS['text_primary']};"
                f" font-size: 9pt;"
            )
