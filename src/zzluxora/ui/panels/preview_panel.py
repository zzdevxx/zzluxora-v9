"""Preview Panel — visual 2D dengan fixture draggable (R1 QLC+ Monitor → Preview).

  - fixture digambar sebagai badge persegi (warna per fixture)
  - bisa di-drag bebas di atas canvas (posisi disimpan)
  - menggambarkan area panggung (garis tepi + label)
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget

from zzluxora.app import AppContext
from zzluxora.ui.styles import COLORS


class _FixtureBadge(QWidget):
    """Badge fixture kecil yang bisa di-drag."""

    moved = Signal()

    def __init__(self, name: str, color: str, parent=None) -> None:
        super().__init__(parent)
        self._name = name
        self._color = QColor(color)
        self.setFixedSize(52, 32)
        self._drag_offset: QPoint | None = None

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setPen(QPen(QColor(COLORS["border_strong"]), 1))
        p.setBrush(self._color)
        p.drawRect(0, 0, 51, 31)
        p.setPen(QPen(QColor("#000000"), 1))
        p.drawText(self.rect(), Qt.AlignCenter, self._name)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and self.parentWidget():
            new_pos = self.parentWidget().mapFromGlobal(event.globalPosition().toPoint())
            new_pos = new_pos - self._drag_offset
            self.move(new_pos)
            self.moved.emit()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None


class PreviewPanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self._badges: list[_FixtureBadge] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        # Canvas panggung
        self.canvas = QWidget()
        self.canvas.setMinimumSize(700, 400)
        self.canvas.setStyleSheet(
            f"background-color: {COLORS['bg_deep']};"
            f" border: 1px solid {COLORS['border']};"
        )
        lay.addWidget(self.canvas, 1)

        colors = [COLORS["accent_blue"], COLORS["ok_green"],
                  COLORS["warn_yellow"], COLORS["magenta"]]
        names = [f"PAR{i+1}" for i in range(4)]
        for i, name in enumerate(names):
            badge = _FixtureBadge(name, colors[i % len(colors)], parent=self.canvas)
            badge.move(60 + i * 90, 60)
            badge.show()
            self._badges.append(badge)

    # ── API ───────────────────────────────────────────────────────────
    def fixture_count(self) -> int:
        return len(self._badges)

    def fixture_at(self, index: int) -> _FixtureBadge:
        return self._badges[index]
