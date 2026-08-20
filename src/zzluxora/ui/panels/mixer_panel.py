"""Mixer Panel — 512 fader + master (R3 §13, D2).

Fitur flagship:
  - 512 slider DMX (horizontal scroll) + 1 master = 513 total (D2)
  - tiap slider terikat langsung ke core Mixer (channel state)
  - horizontal scroll area: grid 8 baris x 64 kolom per halaman
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.core.mixer import DMX_CHANNELS
from zzluxora.ui.styles import COLORS


class MixerPanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self._sliders: list[QSlider] = []
        self._master: QSlider | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        lay.addWidget(QLabel("DMX MIXER — 512 CHANNELS"))

        # ── Scroll horizontal + vertikal ───────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        grid = QGridLayout(body)
        grid.setHorizontalSpacing(2)
        grid.setVerticalSpacing(2)

        ROWS = 8
        COLS = DMX_CHANNELS // ROWS
        for ch in range(DMX_CHANNELS):
            r, c = ch % ROWS, ch // ROWS
            slider = self._make_slider(ch)
            self._sliders.append(slider)
            grid.addWidget(slider, r, c)
        scroll.setWidget(body)
        lay.addWidget(scroll, 1)

        # ── Master ─────────────────────────────────────────────────────
        master_row = QHBoxLayout()
        master_row.addWidget(QLabel("MASTER"))
        self._master = self._make_slider(-1)
        master_row.addWidget(self._master)
        lay.addLayout(master_row)

    # ── Internals ─────────────────────────────────────────────────────
    def _make_slider(self, ch: int) -> QSlider:
        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 255)
        slider.setFixedWidth(34)
        slider.setValue(self.ctx.mixer.channels[ch] if ch >= 0 else self.ctx.mixer.master)
        if ch >= 0:
            slider.valueChanged.connect(
                lambda val, c=ch: self.ctx.mixer.set_channel(c, val)
            )
        else:
            slider.valueChanged.connect(lambda val: setattr(self.ctx.mixer, "master", val))
        return slider

    # ── Test API ──────────────────────────────────────────────────────
    def slider_count(self) -> int:
        return len(self._sliders)

    def slider_at(self, index: int) -> QSlider:
        return self._sliders[index]

    def master_slider(self) -> QSlider:
        assert self._master is not None
        return self._master
