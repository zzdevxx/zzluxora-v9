"""Scene generator — audio features → Scene objects (R2 §2.1, math_model §6-7).

Segmentasi lagu berdasarkan beat/onset (R2 §2.2.1), lalu setiap segmen
dipetakan ke Scene dengan nilai DRGBW per fixture via VA model + color mapping.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from zzluxora.core.color_mapping import hsv_to_rgb, rgb_to_drgbw
from zzluxora.core.models import Fixture, Scene
from zzluxora.core.va_model import (
    compute_arousal,
    compute_valence,
    normalize_features,
    va_to_hsv,
)

# Segmen dasar: 4 detik per scene (bisa di-refine di UI nanti)
SEGMENT_DURATION_MS = 4000


@dataclass
class SceneSpec:
    name: str
    section: str
    start_ms: int
    end_ms: int
    valence: float
    arousal: float
    rms_n: float = 0.0
    chroma_peak: float = 6.0


def segment_song(duration_s: float, bpm: float) -> list[tuple[int, int]]:
    """Split lagu menjadi segmen [start_ms, end_ms].

    BPM tinggi → segmen lebih pendek (ubah lebih cepat) —
    R2 §8 chase timing: >120 → 500ms per scene, 90-120 → 700ms, <90 → 1500ms.
    Panjang segmen diskalakan: durasi detik / (bpm-based hits per 4s).
    """
    if duration_s <= 0:
        return []
    # durasi per segmen (ms) mengikuti aturan timing R2 §8
    if bpm > 120:
        per_seg = 500
    elif bpm >= 90:
        per_seg = 700
    else:
        per_seg = 1500
    # gunakan kelipatan beat agar transisi sinkron: 4 ketukan per segmen
    beat_ms = 60000.0 / max(bpm, 1.0)
    seg_ms = max(per_seg, round(beat_ms * 4))
    total_ms = int(duration_s * 1000)
    segs: list[tuple[int, int]] = []
    start = 0
    while start < total_ms:
        end = min(start + seg_ms, total_ms)
        segs.append((start, end))
        start = end
    return segs


def _section_name(index: int, total: int) -> str:
    """Label sections secara sederhana: intro → verse → chorus → bridge → outro."""
    if index == 0:
        return "intro"
    if index >= total - 1:
        return "outro"
    # chorus kira-kira di tengah-tengah lagu
    mid = total / 2.0
    if abs(index + 0.5 - mid) < total * 0.25:
        return "chorus"
    if index % 2 == 0:
        return "verse"
    return "bridge"


def build_scene(spec: SceneSpec, fixtures: list[Fixture]) -> Scene:
    """Satu segmen → Scene dengan DRGBW per fixture (math_model §4-7)."""
    h, s, v = va_to_hsv(spec.valence, spec.arousal, rms_n=spec.rms_n,
                        chroma_peak=spec.chroma_peak)
    r, g, b = hsv_to_rgb(h, s, v)
    drgbw = rgb_to_drgbw(r, g, b, dimmer_from=v)

    values = {f.name: drgbw for f in fixtures}
    return Scene(
        name=spec.name,
        start_ms=spec.start_ms,
        end_ms=spec.end_ms,
        section=spec.section,
        hue=h,
        values=values,
    )


def generate_scenes(features: dict, fixtures: list[Fixture]) -> list[Scene]:
    """Pipeline penuh: raw features → segments → Scenes (R2 §3.1.3)."""
    norm = normalize_features(features)
    arousal = compute_arousal(norm)
    valence = compute_valence(norm)

    bpm = float(features.get("bpm", 90.0))
    duration = float(features.get("duration_s", 0.0))
    segs = segment_song(duration, bpm)

    scenes: list[Scene] = []
    total = len(segs)
    for i, (start_ms, end_ms) in enumerate(segs):
        section = _section_name(i, total)
        spec = SceneSpec(
            name=section.capitalize(),
            section=section,
            start_ms=start_ms,
            end_ms=end_ms,
            valence=valence,
            arousal=arousal,
            rms_n=norm.get("rms", 0.0),
            chroma_peak=float(features.get("chroma_peak", 6.0)),
        )
        scenes.append(build_scene(spec, fixtures))
    return scenes
