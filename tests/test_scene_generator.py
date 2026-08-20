"""Tests for zzluxora.core.scene_generator — segments → Scenes (R2 §2.1/§3)."""
from __future__ import annotations

import pytest

from zzluxora.core.models import DRGBW, Fixture
from zzluxora.core.scene_generator import (
    SEGMENT_DURATION_MS,
    SceneSpec,
    build_scene,
    generate_scenes,
    segment_song,
)


def _feats() -> dict:
    """Feature snapshot mirip lagu worship (Q1 → chorus energik)."""
    return {
        "bpm": 120.0,
        "rms": 0.3,
        "spectral_centroid": 2000.0,
        "mfcc1": 0.0,
        "chroma_major_ratio": 0.7,
        "onset_rate": 2.0,
        "beat_times": [0.5, 1.0, 1.5, 2.0],
        "duration_s": 8.0,
    }


def _fixtures() -> list[Fixture]:
    return [Fixture(name="PAR1", types=["Dimmer", "Red", "Green", "Blue"]),
            Fixture(name="PAR2", types=["Dimmer", "Red", "Green", "Blue"])]


def test_segment_song_creates_segments() -> None:
    segs = segment_song(duration_s=10.0, bpm=120.0)
    assert len(segs) >= 1
    for s in segs:
        assert s[0] >= 0 and s[1] > s[0]
        assert s[1] <= 10000


def test_segment_duration_constant() -> None:
    assert SEGMENT_DURATION_MS == 4000


def test_segment_speed_varies_with_bpm() -> None:
    slow = segment_song(10.0, bpm=80.0)
    fast = segment_song(10.0, bpm=140.0)
    # BPM tinggi → segmen lebih pendek (perubahan lebih cepat)
    assert first_len(fast) < first_len(slow)


def first_len(segs) -> int:
    return segs[0][1] - segs[0][0]


def test_build_scene_has_drgbw_per_fixture() -> None:
    spec = SceneSpec(name="Chorus", section="chorus",
                     start_ms=0, end_ms=4000, valence=0.8, arousal=0.7, rms_n=0.4)
    scene = build_scene(spec, _fixtures())
    assert len(scene.values) == 2
    for v in scene.values.values():
        assert isinstance(v, DRGBW)


def test_build_scene_hue_recorded() -> None:
    spec = SceneSpec(name="V", section="verse", start_ms=0, end_ms=4000,
                     valence=0.3, arousal=0.3, rms_n=0.1)
    scene = build_scene(spec, _fixtures())
    assert 0.0 <= scene.hue <= 360.0


def test_generate_scenes_from_feats() -> None:
    scenes = generate_scenes(_feats(), _fixtures())
    assert len(scenes) >= 1
    names = {s.name for s in scenes}
    assert "Chorus" in names or "Verse" in names


def test_generate_scenes_deterministic() -> None:
    s1 = generate_scenes(_feats(), _fixtures())
    s2 = generate_scenes(_feats(), _fixtures())
    assert [s.name for s in s1] == [s.name for s in s2]
