"""Settings Panel (R3 §21 — data di AppData, R4 — IP default).

  - Target IP (default dari config; R4: universe 0 / port 6454 fixed)
  - SAVE → tulis config.ini ke AppData\\zzluxora
  - Menampilkan path data (R3 §21)
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.ui.styles import COLORS


class SettingsPanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.addWidget(QLabel("SETTINGS"))

        form = QFormLayout()
        self.ip_edit = QLineEdit(self.ctx.cfg.artnet_default_ip)
        self.ip_edit.setObjectName("settingsIpEdit")
        form.addRow("Art-Net Target IP:", self.ip_edit)

        path_lbl = QLabel(str(ctx.cfg.data_dir))
        path_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 8pt;")
        form.addRow("Data directory:", path_lbl)
        lay.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_save = QPushButton("SAVE")
        self.btn_save.setObjectName("settingsSaveBtn")
        self.btn_save.clicked.connect(
            lambda: self.save(self.ctx.cfg.data_dir / "config.ini")
        )
        btns.addWidget(self.btn_save)
        lay.addLayout(btns)
        lay.addStretch(1)

    def save(self, path: Path) -> None:
        self.ctx.cfg.artnet_default_ip = self.ip_edit.text().strip() or "127.0.0.1"
        self.ctx.cfg.save(path)
