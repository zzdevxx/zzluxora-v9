"""Tests for frame loop — mixer DMX → ArtNet sender (live output)."""
from __future__ import annotations

import pytest

from zzluxora.core.mixer import Mixer
from zzluxora.services.artnet_service import ArtNetService


class FakeSender:
    def __init__(self) -> None:
        self.last_dmx: list[int] | None = None
        self.sends = 0
        self.target_ip = "127.0.0.1"

    def send(self, dmx: list[int]) -> None:
        self.last_dmx = list(dmx)
        self.sends += 1

    def blackout(self) -> None:
        self.last_dmx = [0] * 512
        self.sends += 1

    def close(self) -> None:
        pass


def test_tick_sends_mixer_dmx() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    mixer = Mixer()
    mixer.set_channel(0, 255)
    mixer.set_channel(1, 128)
    svc.connect()
    svc.tick(33, dmx=mixer.get_dmx())
    assert fake.sends == 1
    assert fake.last_dmx[0] == 255
    assert fake.last_dmx[1] == 128


def test_tick_disconnected_no_send() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    mixer = Mixer()
    svc.tick(33, dmx=mixer.get_dmx())
    assert fake.sends == 0


def test_tick_without_dmx_uses_placeholder() -> None:
    """Backward compat: tanpa dmx → placeholder nol (test lama tetap hijau)."""
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    svc.connect()
    svc.tick(33)
    assert fake.sends == 1
    assert fake.last_dmx == [0] * 512
