"""Program — multi-track cue sequencer (R1 Function Manager / program editor).

Setiap Track adalah daftar Cue (scene + timing) yang berjalan paralel
seperti track pada program editor v7 (multi-track dengan per-cue colors).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from zzluxora.core.models import Cue


@dataclass
class Track:
    name: str
    cues: list[Cue] = field(default_factory=list)
    current_index: int = 0
    elapsed_ms: int = 0
    loop: bool = True

    def step(self, dt_ms: int) -> None:
        if not self.cues:
            return
        self.elapsed_ms += dt_ms
        hold = self.cues[self.current_index].hold_ms
        while self.elapsed_ms >= hold:
            self.elapsed_ms -= hold
            if self.current_index + 1 >= len(self.cues):
                if self.loop:
                    self.current_index = 0
                else:
                    self.current_index = len(self.cues) - 1
                    self.elapsed_ms = 0
                    return
            else:
                self.current_index += 1
            hold = self.cues[self.current_index].hold_ms

    def current_cue(self) -> Cue | None:
        if not self.cues:
            return None
        return self.cues[self.current_index]


@dataclass
class Program:
    tracks: list[Track] = field(default_factory=list)
    active_track: str = ""

    def __post_init__(self) -> None:
        if self.tracks and not self.active_track:
            self.active_track = self.tracks[0].name

    def step(self, dt_ms: int) -> None:
        for track in self.tracks:
            track.step(dt_ms)

    def set_active(self, name: str) -> None:
        self.active_track = name

    def get_track(self, name: str) -> Track | None:
        for t in self.tracks:
            if t.name == name:
                return t
        return None
