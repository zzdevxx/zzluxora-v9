"""Address Panel — DMX addressing grid + Auto Patch / Clear All (R3 §8)."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.core.models import make_par_rgbw_8ch
from zzluxora.ui.styles import COLORS
from zzluxora.ui.widgets.address_grid import AddressGrid


class AddressPanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        # Toolbar
        bar = QHBoxLayout()
        title = QLabel("DMX ADDRESS")
        title.setStyleSheet(f"font-weight: 700; color: {COLORS['text_primary']};")
        bar.addWidget(title)
        bar.addStretch(1)

        self.btn_auto_patch = QPushButton("AUTO PATCH")
        self.btn_auto_patch.setObjectName("autoPatchBtn")
        self.btn_auto_patch.setStyleSheet(
            f"background-color: {COLORS['accent_blue']}; color: #000000;"
        )
        self.btn_auto_patch.clicked.connect(self.auto_patch)
        bar.addWidget(self.btn_auto_patch)

        self.btn_clear_all = QPushButton("CLEAR ALL")
        self.btn_clear_all.setObjectName("clearAllBtn")
        self.btn_clear_all.clicked.connect(self.clear_all)
        bar.addWidget(self.btn_clear_all)
        lay.addLayout(bar)

        self.grid = AddressGrid(rows=8)
        lay.addWidget(self.grid, 1)

        self.grid.cellClicked.connect(self._on_cell)
        self._patch_default()

    # ------------------------------------------------------------------
    def _patch_default(self) -> None:
        """Fixture default skripsi: 4x PAR LED RGBW 8-kanal, mulai ch1."""
        for i in range(4):
            ch = 1 + i * 8
            self.grid.set_fixture(ch, make_par_rgbw_8ch(name=f"PAR{i+1}"))

    def auto_patch(self) -> None:
        self.grid.clear_all()
        self._patch_default()

    def clear_all(self) -> None:
        self.grid.clear_all()

    def _on_cell(self, ch: int) -> None:
        # TODO M7: buka Fixture Editor untuk channel terpilih (drag-drop)
        pass
