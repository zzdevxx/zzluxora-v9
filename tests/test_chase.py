"""Tests for zzluxora.core.chase — timing rules (R2 §8) + sequencer (M3)."""
from __future__ import annotations

import pytest

from zzluxora.core.chase import (
    ChaseSequencer,
    cue_hold_ms,
    transition_style,
)


# ---------------------------------------------------------------- timing rules
def test_cue_hold_fast_bpm() -> None:
    # >120 → 500ms (R2 §8)
    assert cue_hold_ms(140.0) == 500


def test_cue_hold_mid_bpm() -> None:
    # 90-120 → 700ms
    assert cue_hold_ms(100.0) == 700


def test_cue_hold_slow_bpm() -> None:
    # <90 → 1500ms
    assert cue_hold_ms(73.0) == 1500


def test_transition_snap_on_high_onset() -> None:
    # onset strength > 0.7 → snap (instant)
    assert transition_style(0.8) == "snap"


def test_transition_crossfade_low_onset() -> None:
    # < 0.3 → crossfade (gradual)
    assert transition_style(0.2) == "crossfade"


def test_transition_mid() -> None:
    assert transition_style(0.5) in ("snap", "crossfade")


# ---------------------------------------------------------------- sequencer
def _seq() -> ChaseSequencer:
    return ChaseSequencer(cue_holds=[500, 500, 500], loop=True)


def test_sequencer_starts_at_first_cue() -> None:
    s = _seq()
    assert s.current_index == 0
    assert s.elapsed_ms == 0


def test_sequencer_advances_after_hold() -> None:
    s = _seq()
    s.step(500)
    assert s.current_index == 1


def test_sequencer_loops() -> None:
    s = _seq()
    s.step(500)
    s.step(500)
    s.step(500)  # back to 0 (3 cues)
    assert s.current_index == 0


def test_sequencer_no_loop_stops() -> None:
    s = ChaseSequencer(cue_holds=[500, 500], loop=False)
    s.step(500)
    s.step(500)
    assert s.done is True


def test_sequencer_forward() -> None:
    s = ChaseSequencer(cue_holds=[300, 300], direction="forward")
    s.step(300)
    assert s.current_index == 1


def test_sequencer_backward() -> None:
    s = ChaseSequencer(cue_holds=[300, 300, 300], direction="backward")
    s.step(300)
    assert s.current_index == 2
    s.step(300)
    assert s.current_index == 1


def test_sequencer_bounce() -> None:
    s = ChaseSequencer(cue_holds=[300, 300, 300], direction="bounce")
    s.step(300)
    assert s.current_index == 1
    s.step(300)
    assert s.current_index == 2
    s.step(300)
    assert s.current_index == 1  # balik, bukan loop ke 0
