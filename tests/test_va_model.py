"""Tests for zzluxora.core.va_model — normalize + Valence/Arousal + V-A→HSV.

Dasar: skripsi v3 (R2) §2.2.3d + script_math_model.md §2-4.
Contoh referensi: "10.000 Reasons" (math_model §9) — BPM 73, RMS 0.08,
SC 1800, MFCC1 -120, onset 1.5, chroma 0.72 → A=0.126, V=0.627.
"""
from __future__ import annotations

import pytest

from zzluxora.core.va_model import (
    NORMALIZE_RANGES,
    compute_arousal,
    compute_valence,
    normalize_features,
    normalize_value,
    va_to_hsv,
)


# ---------------------------------------------------------------- normalize
def test_normalize_clips_to_0_1() -> None:
    assert normalize_value(999, 0, 1) == 1.0
    assert normalize_value(-999, 0, 1) == 0.0


def test_normalize_midpoint() -> None:
    assert normalize_value(0.255, 0.01, 0.5) == pytest.approx(0.5, abs=1e-6)


def test_normalize_bpm_ranges_table() -> None:
    # R2: BPM 60-180
    assert NORMALIZE_RANGES["bpm"] == (60.0, 180.0)
    assert NORMALIZE_RANGES["rms"] == (0.01, 0.5)
    assert NORMALIZE_RANGES["spectral_centroid"] == (500.0, 5000.0)
    assert NORMALIZE_RANGES["mfcc1"] == (-300.0, 100.0)
    assert NORMALIZE_RANGES["onset_rate"] == (0.5, 8.0)
    assert NORMALIZE_RANGES["chroma_major_ratio"] == (0.0, 1.0)


def test_normalize_full_dict() -> None:
    raw = {
        "bpm": 73.0, "rms": 0.08, "spectral_centroid": 1800.0,
        "mfcc1": -120.0, "onset_rate": 1.5, "chroma_major_ratio": 0.72,
    }
    norm = normalize_features(raw)
    # math_model §9 expected normalized values
    assert norm["bpm"] == pytest.approx(0.108, abs=1e-3)
    assert norm["rms"] == pytest.approx(0.143, abs=1e-3)
    assert norm["spectral_centroid"] == pytest.approx(0.289, abs=1e-3)
    assert norm["mfcc1"] == pytest.approx(0.45, abs=1e-3)
    assert norm["onset_rate"] == pytest.approx(0.133, abs=1e-3)
    assert norm["chroma_major_ratio"] == pytest.approx(0.72, abs=1e-3)


# ---------------------------------------------------------------- arousal/valence
def test_arousal_10k_reasons() -> None:
    # math_model §9: 0.40*0.108 + 0.35*0.143 + 0.25*0.133 = 0.126
    norm = {"bpm": 0.108, "rms": 0.143, "onset_rate": 0.133}
    assert compute_arousal(norm) == pytest.approx(0.126, abs=1e-3)


def test_valence_10k_reasons() -> None:
    # math_model §9: 0.50*0.720 + 0.30*0.289 + 0.20*0.900 = 0.627
    norm = {"chroma_major_ratio": 0.720, "spectral_centroid": 0.289, "mfcc1": 0.450}
    assert compute_valence(norm) == pytest.approx(0.627, abs=1e-3)


def test_arousal_max_and_min() -> None:
    assert compute_arousal({"bpm": 1, "rms": 1, "onset_rate": 1}) == pytest.approx(1.0)
    assert compute_arousal({"bpm": 0, "rms": 0, "onset_rate": 0}) == pytest.approx(0.0)


def test_valence_max_and_min() -> None:
    assert compute_valence({"chroma_major_ratio": 1, "spectral_centroid": 1, "mfcc1": 0.5}) == pytest.approx(1.0)
    assert compute_valence({"chroma_major_ratio": 0, "spectral_centroid": 0, "mfcc1": 0.0}) == pytest.approx(0.0)


# ---------------------------------------------------------------- VA -> HSV
def test_q1_praise_warm() -> None:
    # V>0.5, A>0.5 → hue 30..90 (kuning/amber) — R2 §7.2
    h, s, v = va_to_hsv(0.8, 0.8)
    assert 30 <= h <= 90


def test_q2_intense_magenta() -> None:
    # V<=0.5, A>0.5 → 270..330 (ungu/magenta)
    h, _, _ = va_to_hsv(0.3, 0.8)
    assert 270 <= h <= 330


def test_q3_contemplative_blue() -> None:
    # V<=0.5, A<=0.5 → 200..260 (biru/indigo)
    h, _, _ = va_to_hsv(0.3, 0.3)
    assert 200 <= h <= 260


def test_q4_peaceful_cyan() -> None:
    # V>0.5, A<=0.5 → 150..200 (hijau/cyan)
    h, _, _ = va_to_hsv(0.7, 0.3)
    assert 150 <= h <= 200


def test_hue_chroma_correction() -> None:
    # H = H_base + (ChromaPeak - 6) * 5° — chroma peak 6+ = shift hangat
    h, _, _ = va_to_hsv(0.8, 0.8, chroma_peak=8)
    h_base, _, _ = va_to_hsv(0.8, 0.8, chroma_peak=6)
    assert h == pytest.approx(h_base + 10.0)


def test_saturation_formula() -> None:
    _, s, _ = va_to_hsv(0.5, 0.5)
    # S = 0.6*0.5 + 0.4*|2*0.5-1| = 0.3 + 0 = 0.3
    assert s == pytest.approx(0.3, abs=1e-6)


def test_value_floor_010() -> None:
    _, _, v = va_to_hsv(0.0, 0.0)
    assert v >= 0.10


def test_value_formula() -> None:
    # V = max(0.5*rms_n + 0.5*A, 0.10); dengan A sebagai aproksimasi
    _, _, v = va_to_hsv(0.5, 0.5, rms_n=0.5)
    assert v == pytest.approx(0.5, abs=1e-6)
