"""MATH MODEL REGRESSION — RELEASE BLOCKER (18 tests).

Pipeline inti skripsi: audio features → normalize → V-A → HSV → RGB → RGBW → DRGBW.
Diambil dari skripsi BAB 3 + script_math_model.md. Setiap test harus pass
sebelum rilis (sama seperti v7's tests/test_math_model.py).

Terbagi 6 kelompok sesuai README v7:
  1) 10k Reasons validation (audio→RGBW math)
  2) V/A quadrant mapping
  3) HSV→RGB conversion
  4) RGB→RGBW extraction
  5) Chase timing
  6) Pattern selection (dikover di test_math_model via rules)
"""
from __future__ import annotations

import numpy as np
import pytest

from zzluxora.core.chase import ChaseSequencer, cue_hold_ms
from zzluxora.core.color_mapping import hsv_to_rgb, rgb_to_rgbw
from zzluxora.core.models import Fixture
from zzluxora.core.scene_generator import generate_scenes
from zzluxora.core.va_model import (
    compute_arousal,
    compute_valence,
    normalize_features,
    va_to_hsv,
)


# =====================================================================
# 1) 10k Reasons validation — contoh skripsi (math_model §9)
# =====================================================================
def test_10k_normalization_values():
    norm = normalize_features({
        "bpm": 73.0, "rms": 0.08, "spectral_centroid": 1800.0,
        "mfcc1": -120.0, "onset_rate": 1.5, "chroma_major_ratio": 0.72,
    })
    assert norm["bpm"] == pytest.approx(0.108, abs=1e-3)
    assert norm["rms"] == pytest.approx(0.143, abs=1e-3)


def test_10k_arousal_formula():
    a = compute_arousal({"bpm": 0.108, "rms": 0.143, "onset_rate": 0.133})
    assert a == pytest.approx(0.126, abs=1e-3)


def test_10k_valence_formula():
    v = compute_valence({"chroma_major_ratio": 0.72, "spectral_centroid": 0.289,
                         "mfcc1": 0.45})
    assert v == pytest.approx(0.627, abs=1e-3)


def test_10k_lands_q4_peaceful():
    h, _, _ = va_to_hsv(0.627, 0.126)
    assert 150 <= h <= 200  # cyan (Q4 damai/tenang) — sesuai math_model §9


def test_10k_drgbw_warm_white():
    h, s, v = va_to_hsv(0.627, 0.126, rms_n=0.143)
    r, g, b = hsv_to_rgb(h, s, v)
    dr, dg, db, w = rgb_to_rgbw(r, g, b)
    assert w >= dr and w >= dg and w >= db  # dominan white (lagu worship redup)


# =====================================================================
# 2) V/A quadrant mapping (R2 §7.2)
# =====================================================================
def test_q1_praise_yellow():
    h, s, _ = va_to_hsv(0.8, 0.8)
    assert 30 <= h <= 90 and s > 0.5


def test_q2_intense_magenta():
    h, s, _ = va_to_hsv(0.3, 0.8)
    assert 270 <= h <= 330 and s > 0.5


def test_q3_contemplative_blue():
    h, _, _ = va_to_hsv(0.3, 0.3)
    assert 200 <= h <= 260


def test_q4_peaceful_cyan():
    h, s, _ = va_to_hsv(0.7, 0.3)
    assert 150 <= h <= 200 and s < 0.5  # lembut


# =====================================================================
# 3) HSV→RGB conversion (Foley & van Dam)
# =====================================================================
def test_hsv_rgb_primary_red():
    assert hsv_to_rgb(0, 1, 1) == (255, 0, 0)


def test_hsv_rgb_primary_green():
    assert hsv_to_rgb(120, 1, 1) == (0, 255, 0)


def test_hsv_rgb_primary_blue():
    assert hsv_to_rgb(240, 1, 1) == (0, 0, 255)


def test_hsv_rgb_white_and_black():
    assert hsv_to_rgb(0, 0, 1) == (255, 255, 255)
    assert hsv_to_rgb(0, 1, 0) == (0, 0, 0)


# =====================================================================
# 4) RGB→RGBW extraction
# =====================================================================
def test_rgbw_white_is_min():
    assert rgb_to_rgbw(200, 100, 50) == (150, 50, 0, 50)


def test_rgbw_pure_and_gray():
    assert rgb_to_rgbw(255, 0, 0) == (255, 0, 0, 0)
    assert rgb_to_rgbw(128, 128, 128) == (0, 0, 0, 128)


# =====================================================================
# 5) Chase timing (R2 §8)
# =====================================================================
def test_chase_timing_bpm_bands():
    assert cue_hold_ms(140) == 500
    assert cue_hold_ms(100) == 700
    assert cue_hold_ms(73) == 1500


def test_chase_sequencer_advance_and_loop():
    s = ChaseSequencer(cue_holds=[500, 500, 500])
    s.step(500)
    s.step(500)
    s.step(500)
    assert s.current_index == 0


# =====================================================================
# 6) Scene generation pipeline (audio→DRGBW per fixture)
# =====================================================================
def test_scene_pipeline_deterministic():
    feats = {"bpm": 120, "rms": 0.3, "spectral_centroid": 2000, "mfcc1": 0.0,
             "chroma_major_ratio": 0.7, "onset_rate": 2.0,
             "beat_times": [0.5], "duration_s": 8.0}
    fix = [Fixture(name="PAR1", types=["Dimmer", "Red", "Green", "Blue"])]
    s1 = generate_scenes(feats, fix)
    s2 = generate_scenes(feats, fix)
    assert [(sc.name, sc.hue, sc.values["PAR1"].as_tuple()) for sc in s1] == \
           [(sc.name, sc.hue, sc.values["PAR1"].as_tuple()) for sc in s2]


def test_scene_pipeline_drgbw_8bit():
    feats = {"bpm": 90, "rms": 0.1, "spectral_centroid": 1000, "mfcc1": -50,
             "chroma_major_ratio": 0.5, "onset_rate": 1.0,
             "beat_times": [], "duration_s": 4.0}
    fix = [Fixture(name="PAR1", types=["Dimmer", "Red", "Green", "Blue", "Empty", "Program", "Speed"])]
    scenes = generate_scenes(feats, fix)
    for sc in scenes:
        drgbw = sc.values["PAR1"]
        for val in drgbw.as_tuple():
            assert 0 <= val <= 255
