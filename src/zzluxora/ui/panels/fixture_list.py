"""Fixture List Panel (R1 QLC+ Fixture Manager → list + drag).

  - daftar fixture dengan jumlah channel (8ch, 4ch, dst)
  - ADD FIXTURE / REMOVE
  - item drag-able ke Address grid (M7 drag-drop ke address)
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.core.models import make_par_rgbw_8ch
from zzluxora.ui.styles import COLORS


class FixtureListPanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("FIXTURES"))
        bar.addStretch(1)

        self.btn_add = QPushButton("ADD FIXTURE")
        self.btn_add.setObjectName("addFixtureBtn")
        self.btn_add.clicked.connect(
            lambda: self.add_fixture(f"PAR{self.count()+1}",
                                     ["Dimmer", "Red", "Green", "Blue"])
        )
        bar.addWidget(self.btn_add)

        self.btn_remove = QPushButton("REMOVE")
        self.btn_remove.setObjectName("removeFixtureBtn")
        self.btn_remove.clicked.connect(self.remove_selected)
        bar.addWidget(self.btn_remove)
        lay.addLayout(bar)

        self.list = QListWidget()
        lay.addWidget(self.list, 1)

        # Default fixtures (skripsi: 4x PAR RGBW 8-kanal)
        for i in range(4):
            self._append_item(f"PAR{i+1}", make_par_rgbw_8ch(name=f"PAR{i+1}"))

    # ── API ───────────────────────────────────────────────────────────
    def _append_item(self, name: str, fixture) -> None:
        n_ch = len(fixture.types)
        item = QListWidgetItem(f"{name}  ({n_ch}ch)")
        item.setData(Qt.UserRole, fixture)
        self.list.addItem(item)

    def count(self) -> int:
        return self.list.count()

    def item(self, index: int) -> QListWidgetItem:
        return self.list.item(index)

    def add_fixture(self, name: str, types: list[str]) -> None:
        from zzluxora.core.models import Fixture
        self._append_item(name, Fixture(name=name, types=types))

    def remove_selected(self) -> None:
        row = self.list.currentRow()
        if row >= 0:
            self.list.takeItem(row)

    def refresh_from_ctx(self) -> None:
        """Reload list dari ctx.fixtures (dipanggil setelah Open Project)."""
        self.list.clear()
        for fixture in self.ctx.fixtures:
            self._append_item(fixture.name, fixture)
