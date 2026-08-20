"""DMX Address Grid (R3 §8 — grid 24 cells/row).

  - max 24 kotak per baris, scroll vertikal
  - sel kosong: tampil angka address (pojok kecil)
  - sel terisi: label fixture + angka address (warna per tipe channel)
  - klik sel kosong → selected_channel (untuk Auto Patch)
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QScrollArea,
    QWidget,
)

from zzluxora.core.models import Fixture
from zzluxora.ui.styles import COLORS

MAX_COLS = 24  # R3 §8
CELL_W, CELL_H = 84, 40

# Warna per tipe channel (R3 §8: Dimmer=ikon lampu, Red=blok merah)
CHANNEL_COLORS = {
    "Dimmer": COLORS["warn_yellow"],
    "Red": "#E74C3C",
    "Green": "#2ECC71",
    "Blue": "#5C96FD",
    "Strobe": COLORS["magenta"],
    "Program": COLORS["magenta"],
    "Speed": COLORS["accent_cyan"],
    "Empty": COLORS["text_dim"],
}


class AddressGrid(QScrollArea):
    """Grid alamat DMX — scrollable, 24 kolom, klik untuk pilih channel."""

    cellClicked = Signal(int)  # channel 1-based

    def __init__(self, rows: int = 8, parent=None) -> None:
        super().__init__(parent)
        self.cols = MAX_COLS
        self.row_count = rows
        self.selected_channel: int | None = None
        self._fixtures: dict[int, Fixture] = {}  # channel → fixture

        body = QWidget()
        self._grid = QGridLayout(body)
        self._grid.setContentsMargins(6, 6, 6, 6)
        self._grid.setHorizontalSpacing(3)
        self._grid.setVerticalSpacing(3)
        self._cells: list[list[QLabel]] = []
        for r in range(rows):
            row: list[QLabel] = []
            for c in range(self.cols):
                label = self._make_cell(r, c)
                row.append(label)
                self._grid.addWidget(label, r, c)
            self._cells.append(row)
        self.setWidget(body)
        self.setWidgetResizable(True)

    # ------------------------------------------------------------------
    def _make_cell(self, r: int, c: int) -> QLabel:
        ch = r * self.cols + c + 1
        label = QLabel(str(ch))
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(CELL_W, CELL_H)
        label.setStyleSheet(
            f"QLabel {{ background-color: {COLORS['bg_panel']};"
            f" border: 1px solid {COLORS['border']};"
            f" color: {COLORS['text_dim']}; font-size: 9pt; }}"
        )
        label.mousePressEvent = lambda e, ch=ch: self._on_click(ch)
        return label

    def _on_click(self, ch: int) -> None:
        self.selected_channel = ch
        self.cellClicked.emit(ch)

    # ------------------------------------------------------------------
    def cell_widget(self, r: int, c: int) -> QLabel:
        return self._cells[r][c]

    def set_fixture(self, channel: int, fixture: Fixture) -> None:
        """Letakkan fixture mulai channel (1-based), warnai per tipe."""
        self._fixtures[channel] = fixture
        for i, ch_type in enumerate(fixture.types):
            abs_ch = channel + i
            r = (abs_ch - 1) // self.cols
            c = (abs_ch - 1) % self.cols
            if r < self.row_count:
                color = CHANNEL_COLORS.get(ch_type, COLORS["text_secondary"])
                label = self._cells[r][c]
                text = f"{fixture.name}\n{abs_ch}" if i == 0 else fixture.name
                label.setText(text)
                label.setStyleSheet(
                    f"QLabel {{ background-color: {color};"
                    f" border: 1px solid {COLORS['border_strong']};"
                    f" color: #000000; font-size: 9pt; font-weight: 600; }}"
                )

    def clear_all(self) -> None:
        """Hapus semua fixture (R3 §8 — Clear All confirm)."""
        self._fixtures.clear()
        for r in range(self.row_count):
            for c in range(self.cols):
                ch = r * self.cols + c + 1
                label = self._cells[r][c]
                label.setText(str(ch))
                label.setStyleSheet(
                    f"QLabel {{ background-color: {COLORS['bg_panel']};"
                    f" border: 1px solid {COLORS['border']};"
                    f" color: {COLORS['text_dim']}; font-size: 9pt; }}"
                )

    def fixtures(self) -> dict[int, Fixture]:
        return dict(self._fixtures)
