"""Tests for zzluxora.core.artnet_sender — ArtDmx packet (R4 artnet_dmx_v4).

Referensi firmware ESP32 (artnet_dmx_v4.txt §343-358):
  - header "Art-Net\0" (8 bytes)
  - packetBuffer[9] == 0x50 → OpCode ArtDmx (low byte 0x50, high 0x00)
  - universe di packetBuffer[14]
  - length di packetBuffer[16..17] (big endian)
  - data mulai packetBuffer[18]
Port 6454, universe 0 (R4).
"""
from __future__ import annotations

import socket

import pytest

from zzluxora.core.artnet_sender import ArtNetSender, build_artdmx_packet

ARTNET_HEADER = b"Art-Net\x00"


# ---------------------------------------------------------------- packet build
def test_packet_header_artnet() -> None:
    pkt = build_artdmx_packet(dmx=[0] * 512)
    assert pkt[:8] == ARTNET_HEADER


def test_packet_opcode_artdmx() -> None:
    pkt = build_artdmx_packet(dmx=[0] * 512)
    # opcode 0x5000 LE → bytes [8]=0x00, [9]=0x50 (R4 cek packetBuffer[9]==0x50)
    assert pkt[8] == 0x00
    assert pkt[9] == 0x50


def test_packet_universe_zero() -> None:
    pkt = build_artdmx_packet(dmx=[0] * 512)
    # R4: incomingUniverse = packetBuffer[14]; ESP32 cek == 0
    assert pkt[14] == 0


def test_packet_length_512_bigendian() -> None:
    pkt = build_artdmx_packet(dmx=[0] * 512)
    # R4: length = (packetBuffer[16] << 8) | packetBuffer[17]
    length = (pkt[16] << 8) | pkt[17]
    assert length == 512


def test_packet_data_payload() -> None:
    dmx = [0] * 512
    dmx[0] = 255
    dmx[511] = 128
    pkt = build_artdmx_packet(dmx=dmx)
    # R4: data mulai packetBuffer[18]
    assert pkt[18] == 255
    assert pkt[18 + 511] == 128


def test_packet_total_length() -> None:
    pkt = build_artdmx_packet(dmx=[0] * 512)
    assert len(pkt) == 18 + 512  # header 18 + data 512


def test_packet_data_truncated_to_512() -> None:
    pkt = build_artdmx_packet(dmx=[7] * 600)
    assert len(pkt) == 18 + 512


# ---------------------------------------------------------------- sender (mock socket)
class MockSocket:
    """Dummy socket yang mencatat sendto calls."""

    def __init__(self) -> None:
        self.sent: list[tuple[bytes, tuple]] = []

    def sendto(self, data: bytes, addr: tuple) -> int:
        self.sent.append((data, addr))
        return len(data)

    def close(self) -> None:
        pass


def test_sender_sends_to_correct_addr(monkeypatch) -> None:
    mock = MockSocket()

    def fake_socket(*args, **kwargs):
        return mock

    monkeypatch.setattr(socket, "socket", fake_socket)
    sender = ArtNetSender(target_ip="192.168.4.1", port=6454)
    sender.send(dmx=[0] * 512)
    assert len(mock.sent) == 1
    addr = mock.sent[0][1]
    assert addr[0] == "192.168.4.1"
    assert addr[1] == 6454


def test_sender_frame_counter_increments() -> None:
    mock = MockSocket()

    def fake_socket(*args, **kwargs):
        return mock

    import zzluxora.core.artnet_sender as mod

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(mod.socket, "socket", fake_socket)
    sender = ArtNetSender(target_ip="127.0.0.1")
    sender.send(dmx=[0] * 512)
    sender.send(dmx=[0] * 512)
    assert sender.frame_counter == 2
    monkeypatch.undo()


def test_sender_blackout_sends_zeros() -> None:
    mock = MockSocket()

    def fake_socket(*args, **kwargs):
        return mock

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(socket, "socket", fake_socket)
    sender = ArtNetSender(target_ip="127.0.0.1")
    sender.blackout()
    pkt = mock.sent[0][0]
    assert all(b == 0 for b in pkt[18:])
