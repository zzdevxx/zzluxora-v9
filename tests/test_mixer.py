"""Tests for zzluxora.core.mixer — 512 ch + master (R3 §13, §3 blackout)."""
from __future__ import annotations

import pytest

from zzluxora.core.mixer import Mixer


def test_mixer_512_channels() -> None:
    m = Mixer()
    assert len(m.channels) == 512
    assert all(c == 0 for c in m.channels)


def test_master_default_255() -> None:
    m = Mixer()
    assert m.master == 255


def test_set_channel_clamps() -> None:
    m = Mixer()
    m.set_channel(0, 300)
    assert m.channels[0] == 255
    m.set_channel(1, -5)
    assert m.channels[1] == 0


def test_blackout_sets_all_zero() -> None:
    m = Mixer()
    for i in range(512):
        m.set_channel(i, 100)
    m.blackout()
    assert all(c == 0 for c in m.channels)
    assert m.master == 0  # R3 §3: blackout set master + channels ke 0


def test_get_dmx_with_master_scaling() -> None:
    m = Mixer()
    m.set_channel(0, 200)
    m.master = 128
    dmx = m.get_dmx()
    # 200 * (128/255) ≈ 100
    assert dmx[0] == pytest.approx(100, abs=2)
    assert len(dmx) == 512


def test_get_dmx_master_full() -> None:
    m = Mixer()
    m.set_channel(3, 255)
    dmx = m.get_dmx()
    assert dmx[3] == 255


def test_reset_master_after_blackout() -> None:
    m = Mixer()
    m.blackout()
    m.master = 255
    m.set_channel(0, 100)
    assert m.get_dmx()[0] == 100
