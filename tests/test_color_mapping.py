"""Tests for zzluxora.core.color_mapping — HSV→RGB→RGBW (R2 §2.2.3b/c)."""
from __future__ import annotations

import pytest

from zzluxora.core.color_mapping import hsv_to_rgb, rgb_to_drgbw, rgb_to_rgbw


# ---------------------------------------------------------------- HSV -> RGB
def test_hsv_red_0deg() -> None:
    r, g, b = hsv_to_rgb(0.0, 1.0, 1.0)
    assert (r, g, b) == pytest.approx((255, 0, 0))


def test_hsv_green_120deg() -> None:
    r, g, b = hsv_to_rgb(120.0, 1.0, 1.0)
    assert (r, g, b) == pytest.approx((0, 255, 0))


def test_hsv_blue_240deg() -> None:
    r, g, b = hsv_to_rgb(240.0, 1.0, 1.0)
    assert (r, g, b) == pytest.approx((0, 0, 255))


def test_hsv_white_sat0() -> None:
    r, g, b = hsv_to_rgb(30.0, 0.0, 1.0)
    assert (r, g, b) == pytest.approx((255, 255, 255))


def test_hsv_black_value0() -> None:
    r, g, b = hsv_to_rgb(30.0, 1.0, 0.0)
    assert (r, g, b) == pytest.approx((0, 0, 0))


def test_hsv_cyan_180deg() -> None:
    r, g, b = hsv_to_rgb(180.0, 1.0, 1.0)
    assert (r, g, b) == pytest.approx((0, 255, 255))


# ---------------------------------------------------------------- RGB -> RGBW
def test_rgbw_white_extraction() -> None:
    # W = min(R,G,B); R'=R-W dst
    r, g, b, w = rgb_to_rgbw(200, 100, 50)
    assert w == 50
    assert (r, g, b) == (150, 50, 0)


def test_rgbw_pure_red_no_white() -> None:
    r, g, b, w = rgb_to_rgbw(255, 0, 0)
    assert w == 0
    assert (r, g, b) == (255, 0, 0)


def test_rgbw_gray_all_white() -> None:
    r, g, b, w = rgb_to_rgbw(128, 128, 128)
    assert w == 128
    assert (r, g, b) == (0, 0, 0)


# ---------------------------------------------------------------- RGB -> DRGBW
def test_drgbw_10k_reasons_example() -> None:
    """math_model §9: V=0.135 → D=34, R=0, G=6, B=4, W=28.

    Pipeline: HSV(162.7, 0.178, 0.135) → RGB → RGBW → dimmer=V*255.
    """
    # Bangun dari HSV langsung (verifikasi konversi terpisah dari VA)
    h, s, v = 162.7, 0.178, 0.135
    r, g, b = hsv_to_rgb(h, s, v)
    rgbw = rgb_to_drgbw(r, g, b, dimmer_from=v)
    # D = round(V*255) = round(34.4) = 34
    assert rgbw.dimmer == pytest.approx(34, abs=1)
    # W = round(min*255) → sekitar 28; RGB kecil
    assert rgbw.white == pytest.approx(28, abs=3)
    assert rgbw.green >= 0 and rgbw.blue >= 0


def test_drgbw_roundtrip_channels() -> None:
    """Verifikasi konsistensi: DRGBW → DMX channel mapping (R2 8-kanal)."""
    d = rgb_to_drgbw(200, 100, 50, dimmer_from=0.8)
    ch = d.to_dmx_channels(8)
    assert ch[0] == d.dimmer  # ch1 dimmer
    assert ch[1] == d.red
    assert ch[2] == d.green
    assert ch[3] == d.blue
    assert ch[4] == 0  # empty
    assert len(ch) == 8
