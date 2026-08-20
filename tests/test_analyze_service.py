"""Tests for zzluxora.services.analyze_service — audio analysis worker (R3 §9)."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from zzluxora.services.analyze_service import (
    ANALYSIS_STEPS,
    AnalyzeWorker,
    analyze_audio_file,
)


@pytest.fixture(scope="module")
def wav_file(tmp_path_factory) -> Path:
    """Sinyal sintetis pendek (2 detik) untuk test cepat."""
    sr = 22050
    t = np.linspace(0, 2.0, int(sr * 2), endpoint=False)
    sig = 0.5 * np.sin(2 * np.pi * 440 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * t))
    path = tmp_path_factory.mktemp("audio") / "test.wav"
    sf.write(str(path), sig, sr)
    return path


def test_analysis_steps_rotate_every_3s() -> None:
    # R3 §9: progress bar description ganti tiap 3 detik
    assert len(ANALYSIS_STEPS) >= 3
    assert "FFT" in ANALYSIS_STEPS[0]


def test_analyze_audio_file_returns_features(wav_file) -> None:
    feats = analyze_audio_file(str(wav_file))
    assert "bpm" in feats
    assert "rms" in feats
    assert "spectral_centroid" in feats
    assert "mfcc1" in feats
    assert "onset_rate" in feats
    assert "duration_s" in feats


def test_analyze_audio_deterministic(wav_file) -> None:
    a = analyze_audio_file(str(wav_file))
    b = analyze_audio_file(str(wav_file))
    assert a["bpm"] == b["bpm"]
    assert a["rms"] == pytest.approx(b["rms"], abs=1e-9)


def test_worker_runs_and_collects(wav_file) -> None:
    worker = AnalyzeWorker(str(wav_file))
    result = []
    worker.finished.connect(lambda feats: result.append(feats))
    worker.run()
    assert len(result) == 1
    assert "bpm" in result[0]


def test_worker_progress_emits(wav_file) -> None:
    worker = AnalyzeWorker(str(wav_file))
    events = []
    worker.progress.connect(lambda pct, desc: events.append((pct, desc)))
    worker.run()
    assert len(events) >= 1
    assert events[0][0] >= 0.0
