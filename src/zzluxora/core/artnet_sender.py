"""Art-Net sender — ArtDmx over UDP (R4 artnet_dmx_v4.txt).

Firmware ESP32 memfilter: header "Art-Net\0", packetBuffer[9]==0x50 (ArtDmx),
universe di packetBuffer[14] harus 0, length di [16..17] (big endian),
data mulai [18]. Port 6454 (R4).

Byte layout ArtDmx:
    [0:8]   "Art-Net\0"
    [8:10]  OpCode 0x5000 (LE) → [8]=0x00, [9]=0x50
    [10:12] ProtVerHi/Lo (0x000E = 14)
    [12:13] Sequence (frame counter)
    [13:14] Physical (0)
    [14:15] Universe (Lo) — universe 0 (R4)
    [15:16] Universe (Hi) — 0
    [16:18] Length (big endian) — 512
    [18:]   DMX data (max 512)
"""
from __future__ import annotations

import socket
from dataclasses import dataclass

ARTNET_HEADER = b"Art-Net\x00"
OPCODE_ARTDMX = 0x5000
PROTOCOL_VERSION = 14  # Art-Net 3/4 protver
ARTNET_PORT = 6454
MAX_DMX = 512


def build_artdmx_packet(
    dmx: list[int],
    universe: int = 0,
    sequence: int = 0,
) -> bytes:
    """Bangun byte packet ArtDmx (R4 byte-layout)."""
    data = bytes(max(0, min(255, int(v))) for v in dmx[:MAX_DMX])
    data = data.ljust(MAX_DMX, b"\x00")

    pkt = bytearray(18 + MAX_DMX)
    pkt[0:8] = ARTNET_HEADER
    pkt[8:10] = OPCODE_ARTDMX.to_bytes(2, "little")
    pkt[10:12] = PROTOCOL_VERSION.to_bytes(2, "little")
    pkt[12] = sequence & 0xFF
    pkt[13] = 0  # physical
    pkt[14] = universe & 0xFF
    pkt[15] = (universe >> 8) & 0xFF
    pkt[16:18] = (len(data)).to_bytes(2, "big")  # R4: big-endian length
    pkt[18:] = data
    return bytes(pkt)


@dataclass
class ArtNetSender:
    """UDP Art-Net sender dengan socket injectable (DIP) untuk testing."""

    target_ip: str = "127.0.0.1"
    port: int = ARTNET_PORT
    universe: int = 0
    frame_counter: int = 0
    _socket: socket.socket | None = None

    def _get_socket(self) -> socket.socket:
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self._socket

    def send(self, dmx: list[int]) -> None:
        pkt = build_artdmx_packet(dmx, universe=self.universe, sequence=self.frame_counter)
        sock = self._get_socket()
        sock.sendto(pkt, (self.target_ip, self.port))
        self.frame_counter = (self.frame_counter + 1) & 0xFF

    def blackout(self) -> None:
        """Kirim semua kanal 0 (R3 §3 — blackout button)."""
        self.send([0] * MAX_DMX)

    def close(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None
