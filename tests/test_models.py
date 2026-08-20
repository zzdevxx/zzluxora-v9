"""Tests for zzluxora.core.models — domain dataclasses (R2 skripsi v3)."""
from __future__ import annotations

import pytest

from zzluxora.core.models import (
    DRGBW,
    Chase,
    Cue,
    Fixture,
    Scene,
    Song,
    make_par_rgbw_8ch,
)


# ---------------------------------------------------------------- DRGBW
def test_drgbw_default_black() -> None:
    d = DRGBW()
    assert d.dimmer == 0 and d.red == 0 and d.green == 0 and d.blue == 0 and d.white == 0


def test_drgbw_clamps_to_0_255() -> None:
    d = DRGBW(dimmer=300, red=-5, green=128, blue=255, white=10)
    assert d.dimmer == 255
    assert d.red == 0
    assert d.green == 128
    assert d.blue == 255
    assert d.white == 10


def test_drgbw_to_dmx_channels() -> None:
    d = DRGBW(dimmer=34, red=0, green=6, blue=4, white=28)
    # R2: 8-kanal PAR = ch1 dimmer, ch2 R, ch3 G, ch4 B, ch5 empty, ch6 program, ch7 speed, ch8 empty
    ch = d.to_dmx_channels(8)
    assert ch[0] == 34
    assert ch[1] == 0
    assert ch[2] == 6
    assert ch[3] == 4
    assert ch[4] == 0  # empty
    assert ch[6] == 0  # speed default


# ---------------------------------------------------------------- Fixture
def test_fixture_default_8ch_par() -> None:
    f = make_par_rgbw_8ch()
    assert f.name == "PAR RGBW 8ch"
    assert f.manufacturer == "ZZLIGHT"
    assert f.channel_count == 8
    assert f.types == ["Dimmer", "Red", "Green", "Blue", "Empty", "Program", "Speed", "Empty"]


def test_fixture_address_defaults_zero() -> None:
    f = make_par_rgbw_8ch()
    assert f.address == 1  # address 1-based DMX


def test_fixture_to_json_roundtrip() -> None:
    f = make_par_rgbw_8ch()
    f.address = 17
    restored = Fixture.from_dict(f.to_dict())
    assert restored == f


def test_fixture_custom_types() -> None:
    f = Fixture(name="Strobe", manufacturer="Test", types=["Dimmer", "Strobe", "Empty"])
    assert f.channel_count == 3
    assert f.types[1] == "Strobe"


# ---------------------------------------------------------------- Scene
def test_scene_has_drgbw_per_fixture() -> None:
    scene = Scene(name="Chorus", start_ms=0, end_ms=5000, values={"1": DRGBW(dimmer=200, red=255)})
    assert scene.values["1"].red == 255
    assert scene.name == "Chorus"


def test_scene_section_label() -> None:
    scene = Scene(name="Verse", section="verse", start_ms=0, end_ms=3000, values={})
    assert scene.section == "verse"


# ---------------------------------------------------------------- Cue / Chase
def test_cue_fields() -> None:
    cue = Cue(scene_id="s1", hold_ms=500, fade_in_ms=100, fade_out_ms=200)
    assert cue.hold_ms == 500
    assert cue.fade_in_ms == 100
    assert cue.fade_out_ms == 200


def test_chase_direction_default_forward() -> None:
    chase = Chase(name="Chase 1", cues=[])
    assert chase.direction == "forward"
    assert chase.loop is True


def test_chase_add_cue_appends() -> None:
    chase = Chase(name="Chase 1", cues=[])
    chase.add_cue(Cue(scene_id="s1"))
    chase.add_cue(Cue(scene_id="s2"))
    assert len(chase.cues) == 2


# ---------------------------------------------------------------- Song
def test_song_fields() -> None:
    song = Song(filepath="C:/songs/10k_reasons.wav", title="10.000 Reasons", duration_s=320.0)
    assert song.title == "10.000 Reasons"
    assert song.duration_s == 320.0
    assert song.features is None  # belum dianalisa


def test_song_has_features_after_analysis() -> None:
    song = Song(filepath="x.wav", title="T")
    song.features = {"bpm": 73.0, "rms": 0.08}
    assert song.features["bpm"] == 73.0
