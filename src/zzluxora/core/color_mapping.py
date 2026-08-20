"""Color mapping — HSV→RGB (Foley & van Dam) → RGBW (R2 §2.2.3b/c).

Pure functions, no Qt. All outputs are 8-bit ints 0..255.
"""
from __future__ import annotations

import colorsys

from zzluxora.core.models import DRGBW


def hsv_to_rgb(hue: float, sat: float, val: float) -> tuple[int, int, int]:
    """Convert HSV (H 0-360, S/V 0-1) to RGB bytes using standard algorithm.

    Uses colorsys (built-in, numerically identical to Foley & van Dam sector
    formula in the skripsi — same C/V/X/m math).
    """
    hue = (hue % 360.0) / 360.0
    sat = max(0.0, min(1.0, float(sat)))
    val = max(0.0, min(1.0, float(val)))
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return round(r * 255), round(g * 255), round(b * 255)


def rgb_to_rgbw(r: int, g: int, b: int) -> tuple[int, int, int, int]:
    """Extract white channel: W = min(R,G,B); R'=R-W, G'=G-W, B'=B-W (R2 §2.2.3c)."""
    r, g, b = (max(0, min(255, int(v))) for v in (r, g, b))
    w = min(r, g, b)
    return r - w, g - w, b - w, w


def rgb_to_drgbw(r: int, g: int, b: int, dimmer_from: float | None = None) -> DRGBW:
    """RGB bytes → DRGBW model. Dimmer = value (0-1) scaled to 0-255."""
    r2, g2, b2, w = rgb_to_rgbw(r, g, b)
    dimmer = round(max(0.0, min(1.0, float(dimmer_from or 0.0))) * 255)
    return DRGBW(dimmer=dimmer, red=r2, green=g2, blue=b2, white=w)
