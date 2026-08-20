"""AppContext — service registry (DI container, ADR-2 pattern v8).

Single source of truth untuk service app-wide:
  config, mixer, artnet sender/service. Panels menerima ctx dan membaca
  service dari sini — tidak ada global singleton tersebar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from zzluxora.config import AppConfig, app_config
from zzluxora.core.artnet_sender import ArtNetSender
from zzluxora.core.mixer import Mixer
from zzluxora.core.models import make_par_rgbw_8ch
from zzluxora.services.artnet_service import ArtNetService


@dataclass
class AppContext:
    cfg: AppConfig = field(default_factory=app_config)
    mixer: Mixer = field(default_factory=Mixer)
    artnet: ArtNetService = field(default_factory=lambda: ArtNetService(sender=ArtNetSender()))

    # Project state
    project_filepath: str | None = None
    project_name: str = "untitled.zlx"
    fixtures: list = field(default_factory=lambda: [
        make_par_rgbw_8ch(name="PAR1"),
        make_par_rgbw_8ch(name="PAR2"),
        make_par_rgbw_8ch(name="PAR3"),
        make_par_rgbw_8ch(name="PAR4"),
    ])

    def __post_init__(self) -> None:
        # Terapkan default dari config (R4: universe 0, ip default)
        sender = self.artnet.sender
        sender.target_ip = self.cfg.artnet_default_ip
        sender.universe = self.cfg.artnet_default_universe

    # ── Project helpers ────────────────────────────────────────────────
    def set_project(self, filepath: str) -> None:
        self.project_filepath = filepath
        self.project_name = Path(filepath).name
