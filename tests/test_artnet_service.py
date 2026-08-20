"""Tests for zzluxora.services.artnet_service — lifecycle (connect/status)."""
from __future__ import annotations

import pytest

from zzluxora.services.artnet_service import ArtNetService


class FakeSender:
    """Injected sender: catat send + blackout."""

    def __init__(self) -> None:
        self.sends = 0
        self.blackouts = 0
        self.closed = False
        self.target_ip = "127.0.0.1"

    def send(self, dmx) -> None:
        self.sends += 1

    def blackout(self) -> None:
        self.blackouts += 1

    def close(self) -> None:
        self.closed = True


def test_service_initial_disconnected() -> None:
    svc = ArtNetService(sender=FakeSender())
    assert svc.status == "disconnected"


def test_tick_disconnected_does_not_send() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    svc.tick(33)
    assert fake.sends == 0


def test_connect_then_tick_sends() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    svc.connect()
    assert svc.status == "connected"
    svc.tick(33)
    assert fake.sends == 1


def test_disconnect_stops_sending() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    svc.connect()
    svc.tick(33)
    svc.disconnect()
    assert svc.status == "disconnected"
    svc.tick(33)
    assert fake.sends == 1  # tidak bertambah


def test_blackout_forwards() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    svc.blackout()
    assert fake.blackouts == 1


def test_connecting_state() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    svc.connecting = True
    svc.status = "connecting"
    assert svc.status == "connecting"


def test_close_closes_sender() -> None:
    fake = FakeSender()
    svc = ArtNetService(sender=fake)
    svc.close()
    assert fake.closed is True
