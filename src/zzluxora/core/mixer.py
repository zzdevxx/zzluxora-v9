"""Mixer — 512 channel DMX + master (R3 §13 mixer tab, §3 blackout).

State murni (core, no Qt). UI fader hanyalah view atas state ini.
Blackout = master & semua channel ke 0 (R3 §3 literal).
"""
from __future__ import annotations

from dataclasses import dataclass, field

DMX_CHANNELS = 512


@dataclass
class Mixer:
    channels: list[int] = field(default_factory=lambda: [0] * DMX_CHANNELS)
    master: int = 255

    def set_channel(self, index: int, value: int) -> None:
        if 0 <= index < DMX_CHANNELS:
            self.channels[index] = max(0, min(255, int(value)))

    def blackout(self) -> None:
        """Set master + semua channel ke 0 (R3 §3)."""
        self.master = 0
        for i in range(DMX_CHANNELS):
            self.channels[i] = 0

    def get_dmx(self) -> list[int]:
        """Kembalikan 512 channel, master scaling diterapkan (0-255)."""
        scale = self.master / 255.0
        return [round(c * scale) for c in self.channels]
