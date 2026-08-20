"""AppConfig — dataclass-backed config with configparser persistence.

Config lives in %APPDATA%\\zzluxora\\config.ini (R3 §21 — user data away from
install dir). Values are typed via a dataclass; save/load round-trips through
an INI file so advanced users can edit it manually.
"""
from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path


def default_data_dir() -> Path:
    """%APPDATA%\\zzluxora — used for config, fixtures, chases, logs."""
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / "zzluxora"
    return Path.home() / ".zzluxora"


@dataclass
class AppConfig:
    # -- Identity (R3 §1) ---
    app_name: str = "zzluxora"
    app_title: str = "ZZLUXORA"
    version: str = "9.0.0"

    # -- Art-Net (R4 — artnet_dmx_v4.txt) --
    # Universe wajib 0, port wajib 6454, single universe.
    artnet_default_ip: str = "127.0.0.1"
    artnet_default_universe: int = 0
    artnet_default_fps: int = 30
    artnet_port: int = 6454

    # -- Behavior ---
    language: str = "en"
    theme: str = "dark"

    # -- Paths (installed app = read-only; data = AppData) --
    data_dir: Path = None  # type: ignore[assignment]  # set in __post_init__

    def __post_init__(self) -> None:
        if self.data_dir is None:
            self.data_dir = default_data_dir()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        parser = configparser.ConfigParser()
        parser["artnet"] = {
            "default_ip": self.artnet_default_ip,
            "universe": str(self.artnet_default_universe),
            "fps": str(self.artnet_default_fps),
            "port": str(self.artnet_port),
        }
        parser["app"] = {
            "language": self.language,
            "theme": self.theme,
        }
        with path.open("w", encoding="utf-8") as fh:
            parser.write(fh)

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        cfg = cls()
        ini = path or (cfg.data_dir / "config.ini")
        if not ini.is_file():
            # Create sensible default on first run.
            cfg.save(ini)
            return cfg
        parser = configparser.ConfigParser()
        parser.read(ini, encoding="utf-8")
        if parser.has_section("artnet"):
            cfg.artnet_default_ip = parser.get("artnet", "default_ip", fallback=cfg.artnet_default_ip)
            cfg.artnet_default_universe = parser.getint("artnet", "universe", fallback=cfg.artnet_default_universe)
            cfg.artnet_default_fps = parser.getint("artnet", "fps", fallback=cfg.artnet_default_fps)
            cfg.artnet_port = parser.getint("artnet", "port", fallback=cfg.artnet_port)
        if parser.has_section("app"):
            cfg.language = parser.get("app", "language", fallback=cfg.language)
            cfg.theme = parser.get("app", "theme", fallback=cfg.theme)
        return cfg


def app_config() -> AppConfig:
    """Convenience singleton — AppContext will own the real instance."""
    return AppConfig.load()
