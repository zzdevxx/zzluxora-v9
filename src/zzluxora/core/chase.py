"""Chase — timing rules (R2 §8) + sequencer engine (R1 Function Manager).

Timing rules per skripsi (math_model §8):
    BPM > 120        → 500 ms per scene (chase running cepat)
    BPM 90-120       → 700 ms
    BPM < 90         → 1500 ms (fade panjang/halus)
    onset > 0.7      → snap (tajam, instant)
    onset < 0.3      → crossfade (halus)
"""
from __future__ import annotations

from dataclasses import dataclass, field


def cue_hold_ms(bpm: float) -> int:
    """Hold time per cue berdasarkan BPM (R2 §8)."""
    if bpm > 120:
        return 500
    if bpm >= 90:
        return 700
    return 1500


def transition_style(onset_strength: float) -> str:
    """Transition: snap jika onset kuat, crossfade jika lemah."""
    if onset_strength > 0.7:
        return "snap"
    if onset_strength < 0.3:
        return "crossfade"
    return "crossfade"  # default halus untuk mid-range


@dataclass
class ChaseSequencer:
    """Time-driven cue stepper. direction: forward|backward|bounce."""

    cue_holds: list[int] = field(default_factory=list)
    direction: str = "forward"
    loop: bool = True
    current_index: int = 0
    elapsed_ms: int = 0
    done: bool = False

    def step(self, dt_ms: int) -> None:
        if self.done or not self.cue_holds:
            return
        self.elapsed_ms += dt_ms
        hold = self.cue_holds[self.current_index]
        while self.elapsed_ms >= hold:
            self.elapsed_ms -= hold
            self._advance()
            if self.done:
                return
            hold = self.cue_holds[self.current_index]

    def _advance(self) -> None:
        n = len(self.cue_holds)
        if self.direction == "forward":
            if self.current_index + 1 >= n:
                if self.loop:
                    self.current_index = 0
                else:
                    self.done = True
            else:
                self.current_index += 1
        elif self.direction == "backward":
            if self.current_index - 1 < 0:
                if self.loop:
                    self.current_index = n - 1
                else:
                    self.done = True
            else:
                self.current_index -= 1
        elif self.direction == "bounce":
            # bounce: maju sampai ujung, lalu balik
            if self.current_index + 1 >= n:
                self.direction = "backward"
                self.current_index = max(0, n - 2)
            else:
                self.current_index += 1
