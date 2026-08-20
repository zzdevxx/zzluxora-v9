"""AnalyzeService — audio analysis worker (R3 §9).

  - Load Audio selalu aktif
  - Analyze/Remove/Export disabled sampai song dipilih
  - progress bar + deskripsi ilmiah ganti tiap 3 detik (R3 §9)
  - Analyze repeatable; Export aktif setelah hasil

Worker berjalan di QThread (tidak blokir UI); core math dari M2
(audio_engine → va_model) yang PURE (no Qt).
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from zzluxora.core.audio_engine import extract_features

# Deskripsi ilmiah yang berputar tiap 3 detik (R3 §9)
ANALYSIS_STEPS = [
    "FFT windowing...",
    "Extracting spectral features...",
    "Tracking BPM with onset envelope...",
    "Computing Mel-frequency cepstrum...",
    "Normalizing to 0-1 range...",
    "Mapping V-A to HSV color space...",
    "Generating DRGBW scenes...",
]


def analyze_audio_file(path: str) -> dict:
    """Wrapper synchronous — core M2 (librosa)."""
    return extract_features(path)


class AnalyzeWorker(QObject):
    """QThread worker: ekstrak fitur + emisi progress."""

    progress = Signal(float, str)  # pct (0-1), description
    finished = Signal(dict)

    def __init__(self, filepath: str, parent=None) -> None:
        super().__init__(parent)
        self.filepath = filepath

    def run(self) -> None:
        try:
            # progress berputar per step (3 detik antar deskripsi di UI)
            steps = len(ANALYSIS_STEPS)
            for i, desc in enumerate(ANALYSIS_STEPS):
                pct = (i + 1) / steps
                self.progress.emit(pct, desc)
            feats = analyze_audio_file(self.filepath)
            self.progress.emit(1.0, "Analysis complete.")
            self.finished.emit(feats)
        except Exception as exc:  # pragma: no cover - propagasi ke panel
            self.finished.emit({"error": str(exc)})
