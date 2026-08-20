"""ArtNetService — connection lifecycle + frame tick (R3 §15, R4).

Orkestrasi: connect/disconnect/blackout + tick(dt) untuk frame loop.
Sender di-inject (DIP) sehingga testable tanpa socket nyata.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class Sender(Protocol):
    target_ip: str

    def send(self, dmx: list[int]) -> None: ...

    def blackout(self) -> None: ...

    def close(self) -> None: ...


@dataclass
class ArtNetService:
    sender: Any  # Sender (injectable — real: ArtNetSender, test: FakeSender)
    status: str = "disconnected"  # connecting | connected | disconnected
    connecting: bool = False

    def connect(self) -> None:
        self.connecting = True
        self.status = "connecting"
        # sinkronisasi: langsung connected (koneksi UDP tidak handshake)
        self.connecting = False
        self.status = "connected"

    def disconnect(self) -> None:
        self.status = "disconnected"

    def tick(self, dt_ms: int = 33, dmx: list[int] | None = None) -> None:
        """Kirim frame jika connected (dipanggil timer ~30 FPS).

        dmx: get_dmx() dari Mixer (512 channel + master scaling).
        Jika None (backward compat), kirim placeholder nol.
        """
        if self.status == "connected":
            frame = dmx if dmx is not None else [0] * 512
            self.sender.send(frame)

    def blackout(self) -> None:
        self.sender.blackout()

    def close(self) -> None:
        self.sender.close()
        self.status = "disconnected"
