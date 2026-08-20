"""Domain models — pure dataclasses mirroring QLC+ engine concepts (R1).

No Qt / UI imports here. These types are the single source of truth shared by
core engines, services and UI panels (replaces the dict soup of v7/v8).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ----------------------------------------------------------------------
# DRGBW — one 8-bit lighting value per fixture channel (R2 skripsi §2.2.4)
# ----------------------------------------------------------------------
@dataclass
class DRGBW:
    """Dimmer, Red, Green, Blue, White — each 0..255.

    Mapping to a DMX fixture: ch1=Dimmer, ch2=R, ch3=G, ch4=B, then any
    extra channels (program, speed, …) default to 0 (R2: 8-kanal PAR).
    """

    dimmer: int = 0
    red: int = 0
    green: int = 0
    blue: int = 0
    white: int = 0

    def __post_init__(self) -> None:
        self.dimmer = _clamp8(self.dimmer)
        self.red = _clamp8(self.red)
        self.green = _clamp8(self.green)
        self.blue = _clamp8(self.blue)
        self.white = _clamp8(self.white)

    def to_dmx_channels(self, channel_count: int = 8) -> list[int]:
        """Map DRGBW onto a fixture's DMX channels (R2 8-kanal layout)."""
        mapping = [self.dimmer, self.red, self.green, self.blue]
        out: list[int] = [0] * channel_count
        for i, val in enumerate(mapping):
            if i < channel_count:
                out[i] = val
        return out

    def as_tuple(self) -> tuple[int, int, int, int, int]:
        return (self.dimmer, self.red, self.green, self.blue, self.white)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"DRGBW(D={self.dimmer},R={self.red},G={self.green},B={self.blue},W={self.white})"


# ----------------------------------------------------------------------
# Fixture — a DMX device definition (R1 Fixture Manager, R2 8-kanal PAR)
# ----------------------------------------------------------------------
@dataclass
class Fixture:
    name: str
    manufacturer: str = "ZZLIGHT"
    types: list[str] = field(default_factory=list)  # per-channel type
    address: int = 1  # DMX start address (1-based)

    @property
    def channel_count(self) -> int:
        return len(self.types)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "types": list(self.types),
            "address": self.address,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Fixture":
        return cls(
            name=str(data["name"]),
            manufacturer=str(data.get("manufacturer", "ZZLIGHT")),
            types=[str(t) for t in data.get("types", [])],
            address=int(data.get("address", 1)),
        )


def make_par_rgbw_8ch(name: str = "PAR RGBW 8ch") -> Fixture:
    """Default fixture from skripsi (R2 §2.2.4): 8 channels PAR LED RGBW."""
    return Fixture(
        name=name,
        manufacturer="ZZLIGHT",
        types=["Dimmer", "Red", "Green", "Blue", "Empty", "Program", "Speed", "Empty"],
    )


# ----------------------------------------------------------------------
# Scene — one lighting state at a moment (R2 def. operasional)
# ----------------------------------------------------------------------
@dataclass
class Scene:
    name: str
    start_ms: int = 0
    end_ms: int = 0
    values: dict[str, DRGBW] = field(default_factory=dict)  # fixture_name -> DRGBW
    section: str = "verse"  # verse | chorus | bridge | intro | outro
    hue: float = 0.0  # informational: source hue for preview


# ----------------------------------------------------------------------
# Cue / Chase — sequence of scenes with timing (R1 Function Manager)
# ----------------------------------------------------------------------
@dataclass
class Cue:
    scene_id: str = ""
    hold_ms: int = 500
    fade_in_ms: int = 100
    fade_out_ms: int = 100


@dataclass
class Chase:
    name: str
    cues: list[Cue] = field(default_factory=list)
    direction: str = "forward"  # forward | backward | bounce
    loop: bool = True
    fps: int = 30

    def add_cue(self, cue: Cue) -> None:
        self.cues.append(cue)


# ----------------------------------------------------------------------
# Song — loaded audio + analysis results (R3 §9 Analyze tab)
# ----------------------------------------------------------------------
@dataclass
class Song:
    filepath: str
    title: str = ""
    duration_s: float = 0.0
    features: Optional[dict[str, float]] = None  # set after Analyze


def _clamp8(value: int) -> int:
    return max(0, min(255, int(value)))
