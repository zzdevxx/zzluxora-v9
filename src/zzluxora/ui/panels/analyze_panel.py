"""Analyze Panel — load audio → analyze → progress → result (R3 §9).

State machine:
  - Load Audio: selalu aktif
  - Analyze/Remove/Export: disabled sampai song dipilih
  - Export: aktif setelah hasil analisis
  - Progress bar + deskripsi ilmiah berganti tiap 3 detik (R3 §9)
  - Analyze repeatable (QThread worker)
"""
from __future__ import annotations

from PySide6.QtCore import QThread, QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.services.analyze_service import ANALYSIS_STEPS, AnalyzeWorker
from zzluxora.ui.styles import COLORS


class AnalyzePanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.song_path: str | None = None
        self.features: dict | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        # ── File row ────────────────────────────────────────────────────
        row = QHBoxLayout()
        self.lbl_song = QLabel("No song loaded")
        self.lbl_song.setStyleSheet(f"color: {COLORS['text_secondary']};")
        row.addWidget(self.lbl_song, 1)

        self.btn_load = QPushButton("LOAD AUDIO")
        self.btn_load.setObjectName("loadBtn")
        self.btn_load.clicked.connect(self.load_song)
        row.addWidget(self.btn_load)

        self.btn_analyze = QPushButton("ANALYZE")
        self.btn_analyze.setObjectName("analyzeBtn")
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self.start_analyze)
        row.addWidget(self.btn_analyze)

        self.btn_remove = QPushButton("REMOVE")
        self.btn_remove.setObjectName("removeBtn")
        self.btn_remove.setEnabled(False)
        self.btn_remove.clicked.connect(self.remove_song)
        row.addWidget(self.btn_remove)

        self.btn_export = QPushButton("EXPORT")
        self.btn_export.setObjectName("exportBtn")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_result)
        row.addWidget(self.btn_export)
        lay.addLayout(row)

        # ── Progress ────────────────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        lay.addWidget(self.progress)

        self.lbl_step = QLabel("")
        self.lbl_step.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        lay.addWidget(self.lbl_step)
        lay.addStretch(1)

        # Timer deskripsi ilmiah — ganti tiap 3 detik (R3 §9)
        self._step_index = 0
        self._step_timer = QTimer(self)
        self._step_timer.setInterval(3000)
        self._step_timer.timeout.connect(self._advance_step_label)
        self._analyzing = False

        self._thread: QThread | None = None
        self._worker: AnalyzeWorker | None = None

    # ── Song selection ────────────────────────────────────────────────
    def load_song(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Audio", "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)",
        )
        if path:
            self.set_song(path)

    def set_song(self, path: str) -> None:
        self.song_path = path
        self.features = None
        self.lbl_song.setText(path.split("/")[-1].split("\\")[-1])
        self._set_state(has_song=True)

    def remove_song(self) -> None:
        self.song_path = None
        self.features = None
        self.lbl_song.setText("No song loaded")
        self.progress.setValue(0)
        self.lbl_step.setText("")
        self._set_state(has_song=False)

    # ── Analyze (QThread) ─────────────────────────────────────────────
    def start_analyze(self) -> None:
        if not self.song_path:
            return
        self._analyzing = True
        self._step_index = 0
        self._step_timer.start()
        self.progress.setValue(0)
        self.btn_analyze.setEnabled(False)
        self.btn_export.setEnabled(False)

        self._thread = QThread(self)
        self._worker = AnalyzeWorker(self.song_path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_analyze_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.start()

    def _advance_step_label(self) -> None:
        if not self._analyzing:
            return
        self.lbl_step.setText(ANALYSIS_STEPS[self._step_index % len(ANALYSIS_STEPS)])
        self._step_index += 1

    def _on_progress(self, pct: float, desc: str) -> None:
        self.progress.setValue(int(pct * 100))
        self.lbl_step.setText(desc)

    def _on_analyze_finished(self, feats: dict) -> None:
        self._analyzing = False
        self._step_timer.stop()
        self.progress.setValue(100)
        if "error" not in feats:
            self.features = feats
            self.ctx.set_last_analysis(feats) if hasattr(self.ctx, "set_last_analysis") else None
        self.btn_analyze.setEnabled(True)  # repeatable (R3 §9)
        self.btn_export.setEnabled("error" not in feats)

    # ── Export ─────────────────────────────────────────────────────────
    def export_result(self) -> None:
        if not self.features:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Scenes", "scenes.json",
                                              "JSON (*.json)")
        if path:
            import json
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.features, fh, indent=2)

    # ── Helpers ────────────────────────────────────────────────────────
    def _set_state(self, has_song: bool) -> None:
        self.btn_analyze.setEnabled(has_song)
        self.btn_remove.setEnabled(has_song)
        self.btn_export.setEnabled(bool(self.features) if has_song else False)
