"""Tests for zzluxora.core.patterns — multi-fixture patterns (R2 §8 pola)."""
from __future__ import annotations

import pytest

from zzluxora.core.models import DRGBW, Fixture
from zzluxora.core.patterns import (
    PATTERNS,
    apply_pattern,
    select_pattern,
)


def _fixtures(n: int = 4) -> list[Fixture]:
    return [Fixture(name=f"PAR{i+1}", types=["Dimmer", "Red", "Green", "Blue"]) for i in range(n)]


def _base() -> DRGBW:
    return DRGBW(dimmer=200, red=255, green=0, blue=0)


# ---------------------------------------------------------------- pattern selection
def test_select_pattern_high_arousal_all_on() -> None:
    # Arousal > 0.7 → All On (R2 §8: energik)
    assert select_pattern(0.8) == "all_on"


def test_select_pattern_fast_praise_running() -> None:
    # BPM > 120 → Running (R2 §8: praise)
    assert select_pattern(0.5, bpm=130) == "running"


def test_select_pattern_low_arousal_gradient() -> None:
    # Arousal < 0.3 → Gradient (R2 §8: tenang)
    assert select_pattern(0.2) == "gradient"


def test_select_pattern_transition_center_out() -> None:
    assert select_pattern(0.5, bpm=100) == "center_out"


def test_patterns_enum() -> None:
    assert set(PATTERNS) == {"all_on", "running", "gradient", "center_out"}


# ---------------------------------------------------------------- apply patterns
def test_all_on_same_everywhere() -> None:
    vals = apply_pattern(_base(), _fixtures(4), "all_on")
    assert len(vals) == 4
    first = vals["PAR1"]
    for v in vals.values():
        assert v == first


def test_running_rotates_brightness() -> None:
    vals = apply_pattern(_base(), _fixtures(4), "running")
    # satu fixture penuh, lainnya redup (hanya fixture aktif yang 200)
    actives = [v for v in vals.values() if v.dimmer > 100]
    assert len(actives) == 1


def test_gradient_decreasing_dimmer() -> None:
    vals = apply_pattern(_base(), _fixtures(4), "gradient")
    dims = [vals[f"PAR{i+1}"].dimmer for i in range(4)]
    assert dims[0] > dims[1] > dims[2] > dims[3]


def test_center_out_middle_bright() -> None:
    vals = apply_pattern(_base(), _fixtures(4), "center_out")
    dims = [vals[f"PAR{i+1}"].dimmer for i in range(4)]
    assert dims[1] >= dims[0] and dims[2] >= dims[3]


def test_apply_pattern_keeps_color() -> None:
    vals = apply_pattern(_base(), _fixtures(4), "all_on")
    for v in vals.values():
        assert v.red == 255  # warna dipertahankan, hanya dimmer berubah
