"""Tests for zzluxora.core.audio_engine — librosa feature extraction (R2 §2.2.1)."""
from __future__ import annotations

import numpy as np
import pytest
import soundfile as sf

from zzluxora.core.audio_engine import extract_features

SR = 22050


@pytest.fixture
def synth_wav(tmp_path) -> str:
    """3-second synthetic WAV: 440Hz sine + amplitude modulation (0.1s click rhythm)."""
    t = np.arange(int(SR * 3.0)) / SR
    signal = 0.5 * np.sin(2 * np.pi * 440 * t)
    # Amplitude envelope: beat-ish pulses every 0.4 s
    envelope = np.clip(np.sin(2 * np.pi * 2.5 * t) + 0.1, 0, 1)
    data = (signal * envelope).astype(np.float32)
    path = tmp_path / "synth.wav"
    sf.write(str(path), data, SR)
    return str(path)


def test_extract_returns_all_required_features(synth_wav) -> None:
    feats = extract_features(synth_wav)
    # R2: BPM, RMS, spectral centroid, MFCC1, chroma major ratio, onset rate, beat
    assert "bpm" in feats
    assert "rms" in feats
    assert "spectral_centroid" in feats
    assert "mfcc1" in feats
    assert "chroma_major_ratio" in feats
    assert "onset_rate" in feats
    assert "beat_times" in feats
    assert "duration_s" in feats


def test_feature_ranges_sane(synth_wav) -> None:
    feats = extract_features(synth_wav)
    assert 0 < feats["bpm"] < 300
    assert 0.0 <= feats["rms"] <= 1.0
    assert 0 < feats["spectral_centroid"] < 20000
    assert -500 < feats["mfcc1"] < 500
    assert 0.0 <= feats["chroma_major_ratio"] <= 1.0
    assert feats["onset_rate"] >= 0.0  # 0 valid untuk audio monoton
    assert feats["duration_s"] == pytest.approx(3.0, abs=0.2)


def test_beat_times_within_duration(synth_wav) -> None:
    feats = extract_features(synth_wav)
    for bt in feats["beat_times"]:
        assert 0.0 <= bt <= feats["duration_s"] + 0.5


def test_deterministic_same_file(synth_wav) -> None:
    f1 = extract_features(synth_wav)
    f2 = extract_features(synth_wav)
    for key in ("bpm", "rms", "spectral_centroid", "mfcc1", "chroma_major_ratio", "onset_rate"):
        assert f1[key] == pytest.approx(f2[key], abs=1e-6)


def test_missing_file_raises(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_features(str(tmp_path / "missing.wav"))
