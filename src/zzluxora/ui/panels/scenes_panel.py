"""Scenes Panel — song analysis → scene cards (R3 §10).

  - kiri: song list (hasil analyze)
  - kanan: scene cards per segmen — label INTRO/VERSE/CHORUS/BRIDGE/OUTRO
    + preview warna DRGBW
  - tombol untuk kirim scene ke Chase (R3 §10 — scene to chase)

Data berasal dari core M2 (scene_generator → build_scene per segmen).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.core.models import Fixture
from zzluxora.core.scene_generator import generate_scenes
from zzluxora.ui.styles import COLORS


class ScenesPanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self._scenes: list = []  # Scene hasil generate_scenes
        self._chase_cues: list = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        # ── Kiri: song list ────────────────────────────────────────────
        left = QVBoxLayout()
        left.addWidget(QLabel("SONGS"))
        self.song_list = QListWidget()
        left.addWidget(self.song_list)
        lay.addLayout(left, 1)

        # ── Kanan: scene cards ─────────────────────────────────────────
        right = QVBoxLayout()
        bar = QHBoxLayout()
        bar.addWidget(QLabel("SCENES"))
        bar.addStretch(1)
        self.btn_to_chase = QPushButton("ADD TO CHASE")
        self.btn_to_chase.setObjectName("toChaseBtn")
        self.btn_to_chase.clicked.connect(self.add_current_to_chase)
        bar.addWidget(self.btn_to_chase)
        right.addLayout(bar)

        self.cards = QWidget()
        self._cards_layout = QVBoxLayout(self.cards)
        self._cards_layout.setSpacing(6)
        from PySide6.QtWidgets import QScrollArea
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self.cards)
        right.addWidget(self._scroll, 1)
        lay.addLayout(right, 3)

    # ── Public ────────────────────────────────────────────────────────
    def set_features(self, feats: dict) -> None:
        fixtures = [Fixture(name=f"PAR{i+1}", types=["Dimmer", "Red", "Green", "Blue"])
                    for i in range(4)]
        self._scenes = generate_scenes(feats, fixtures)
        self.song_list.addItem(feats.get("song_path", "Analyzed song"))
        self._rebuild_cards()

    def scene_count(self) -> int:
        return len(self._scenes)

    def card_labels(self) -> list[str]:
        return [lbl.text() for lbl in self._all_card_labels()]

    def chase_cue_count(self) -> int:
        return len(self._chase_cues)

    def add_current_to_chase(self) -> None:
        if not self._scenes:
            return
        sc = self._scenes[0]  # scene aktif (default pertama)
        self._chase_cues.append({"scene_id": sc.name, "hold_ms": 700})

    # ── Internal ───────────────────────────────────────────────────────
    def _rebuild_cards(self) -> None:
        # hapus cards lama
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for sc in self._scenes:
            self._cards_layout.addWidget(_SceneCard(sc))

    def _all_card_labels(self) -> list[QLabel]:
        labels = []
        for i in range(self._cards_layout.count()):
            w = self._cards_layout.itemAt(i).widget()
            if isinstance(w, _SceneCard):
                labels.append(w.label)
        return labels


class _SceneCard(QWidget):
    """Card per segmen: label section + swatch warna DRGBW."""

    def __init__(self, scene, parent=None) -> None:
        super().__init__(parent)
        self.scene = scene
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)

        self.label = QLabel(scene.name.upper())
        self.label.setStyleSheet(f"font-weight: 700; color: {COLORS['text_primary']};")
        lay.addWidget(self.label)
        lay.addStretch(1)

        # swatch warna (dari scene DRGBW fixture pertama)
        drgbw = scene.values.get("PAR1")
        if drgbw is not None:
            color = QColor(drgbw.red, drgbw.green, drgbw.blue)
            sw = QLabel()
            sw.setFixedSize(28, 18)
            sw.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid {COLORS['border']};"
            )
            lay.addWidget(sw)

        info = QLabel(f"{scene.start_ms}-{scene.end_ms} ms")
        info.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 8pt;")
        lay.addWidget(info)

        self.setStyleSheet(
            f"background-color: {COLORS['bg_panel']};"
            f" border: 1px solid {COLORS['border']}; border-radius: 2px;"
        )
