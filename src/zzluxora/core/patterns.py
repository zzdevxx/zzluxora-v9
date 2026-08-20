"""Multi-fixture patterns (R2 §8 — Pola Multi-Fixture).

    all_on      : semua fixture sama — bagian energik (Arousal > 0.7)
    running     : satu fixture bergantian per beat — praise (BPM > 120)
    gradient    : brightness menurun fixture 1→N — tenang (Arousal < 0.3)
    center_out  : tengah terang, sisi redup — transisi

Semua pola mempertahankan warna (RGBW), hanya memodulasi dimmer.
"""
from __future__ import annotations

from dataclasses import replace

from zzluxora.core.models import DRGBW, Fixture

PATTERNS = ("all_on", "running", "gradient", "center_out")


def select_pattern(arousal: float, bpm: float = 90.0) -> str:
    """Pilih pola berdasarkan Arousal & BPM (R2 §8)."""
    if arousal > 0.7:
        return "all_on"
    if bpm > 120:
        return "running"
    if arousal < 0.3:
        return "gradient"
    return "center_out"


def apply_pattern(base: DRGBW, fixtures: list[Fixture], pattern: str) -> dict[str, DRGBW]:
    """Terapkan pola ke semua fixture. Mengembalikan {fixture_name: DRGBW}."""
    n = len(fixtures)
    if n == 0:
        return {}
    out: dict[str, DRGBW] = {}

    if pattern == "all_on":
        for f in fixtures:
            out[f.name] = base
        return out

    if pattern == "running":
        # satu fixture penuh (yang "aktif"), lainnya redup 20%
        for i, f in enumerate(fixtures):
            if i == 0:
                out[f.name] = base
            else:
                out[f.name] = replace(base, dimmer=max(10, int(base.dimmer * 0.2)))
        return out

    if pattern == "gradient":
        # brightness turun linear dari 100% → 20%
        for i, f in enumerate(fixtures):
            ratio = 1.0 - (0.8 * i / max(n - 1, 1))
            out[f.name] = replace(base, dimmer=max(5, int(base.dimmer * ratio)))
        return out

    if pattern == "center_out":
        # tengah terang, tepi redup (falloff kuadrat dari tengah)
        center = (n - 1) / 2.0
        for i, f in enumerate(fixtures):
            dist = abs(i - center) / max(center, 1.0)
            ratio = 1.0 - 0.7 * min(dist, 1.0)
            out[f.name] = replace(base, dimmer=max(5, int(base.dimmer * ratio)))
        return out

    raise ValueError(f"Unknown pattern: {pattern}")
