"""Tests for zzluxora.core.program — multi-track cue sequencer (R1 Function)."""
from __future__ import annotations

import pytest

from zzluxora.core.models import Cue
from zzluxora.core.program import Program, Track


def _track(name: str = "T1") -> Track:
    return Track(name=name, cues=[Cue(scene_id="a", hold_ms=300), Cue(scene_id="b", hold_ms=300)])


def test_track_add_and_step() -> None:
    t = _track()
    assert len(t.cues) == 2
    t.step(300)
    assert t.current_index == 1


def test_track_loop_wraps() -> None:
    t = _track()
    t.step(300)
    t.step(300)
    assert t.current_index == 0  # loop


def test_program_with_two_tracks() -> None:
    p = Program(tracks=[_track("drums"), _track("vocals")])
    assert len(p.tracks) == 2
    assert p.active_track == "drums"


def test_program_advance_all() -> None:
    p = Program(tracks=[_track("a"), _track("b")])
    p.step(300)
    assert p.tracks[0].current_index == 1
    assert p.tracks[1].current_index == 1


def test_program_set_active() -> None:
    p = Program(tracks=[_track("a"), _track("b")])
    p.set_active("b")
    assert p.active_track == "b"


def test_program_cue_lookup() -> None:
    t = _track()
    cue = t.current_cue()
    assert cue.scene_id == "a"
