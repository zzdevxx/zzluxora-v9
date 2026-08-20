"""About Dialog — info aplikasi & skripsi (Help → About, R3 §4)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from zzluxora.app import AppContext
from zzluxora.ui.styles import COLORS


class AboutDialog(QDialog):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.setWindowTitle("About ZZLUXORA")
        self.setFixedWidth(420)

        lay = QVBoxLayout(self)
        title = QLabel("ZZLUXORA v9.0.0")
        title.setStyleSheet(f"font-size: 16pt; font-weight: 700; color: {COLORS['accent_blue']};")
        lay.addWidget(title)

        desc = QLabel(
            "Audio-Reactive Lighting Design\n"
            "Berdasarkan Analisis Mood Lagu Rohani\n"
            "dengan Pemetaan Warna HSV-RGBW\n"
            "dan Protokol Art-Net DMX512"
        )
        desc.setStyleSheet(f"color: {COLORS['text_secondary']};")
        desc.setAlignment(Qt.AlignCenter)
        lay.addWidget(desc)

        author = QLabel("Andreas Restuawanta Christwara — 5312422036\nTeknik Komputer, UNNES")
        author.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 8pt;")
        author.setAlignment(Qt.AlignCenter)
        lay.addWidget(author)
