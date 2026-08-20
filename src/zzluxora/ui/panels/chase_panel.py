"""Chase Panel — cue timeline (R1 Function Manager / chase editor).

  - daftar cue (scene + hold time)
  - tombol ADD CUE / REMOVE CUE
  - arah: forward / backward / bounce (core ChaseSequencer)
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.ui.styles import COLORS


class ChasePanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self._cues: list[dict] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("CHASE TIMELINE"))

        self.combo_direction = QComboBox()
        self.combo_direction.addItems(["forward", "backward", "bounce"])
        bar.addWidget(self.combo_direction)
        bar.addStretch(1)

        self.btn_add = QPushButton("ADD CUE")
        self.btn_add.setObjectName("addCueBtn")
        self.btn_add.clicked.connect(lambda: self.add_cue(f"Cue {self.cue_count()+1}", 700))
        bar.addWidget(self.btn_add)

        self.btn_remove = QPushButton("REMOVE CUE")
        self.btn_remove.setObjectName("removeCueBtn")
        self.btn_remove.clicked.connect(lambda: self.remove_cue(self.cue_list.currentRow()))
        bar.addWidget(self.btn_remove)
        lay.addLayout(bar)

        self.cue_list = QListWidget()
        lay.addWidget(self.cue_list, 1)

    # ── API ───────────────────────────────────────────────────────────
    def cue_count(self) -> int:
        return len(self._cues)

    def direction(self) -> str:
        return self.combo_direction.currentText()

    def add_cue(self, scene_id: str, hold_ms: int) -> None:
        self._cues.append({"scene_id": scene_id, "hold_ms": hold_ms})
        self.cue_list.addItem(f"{scene_id}  [{hold_ms} ms]")

    def remove_cue(self, index: int) -> None:
        if 0 <= index < len(self._cues):
            self._cues.pop(index)
            self.cue_list.takeItem(index)
