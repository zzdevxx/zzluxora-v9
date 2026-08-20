"""Tests for zzluxora.config — AppConfig dataclass + configparser round-trip."""
from __future__ import annotations

import configparser

import pytest

from zzluxora.config import AppConfig


def test_defaults() -> None:
    cfg = AppConfig()
    assert cfg.app_name == "zzluxora"
    assert cfg.artnet_default_ip == "127.0.0.1"
    assert cfg.artnet_default_universe == 0
    assert cfg.artnet_default_fps == 30
    assert cfg.language == "en"
    assert cfg.theme == "dark"


def test_artnet_required_for_dmx() -> None:
    """Universe wajib 0 dan port wajib 6454 (R4 — artnet_dmx_v4)."""
    cfg = AppConfig()
    assert cfg.artnet_port == 6454
    assert cfg.artnet_default_universe == 0


def test_roundtrip_save_load(tmp_path) -> None:
    cfg = AppConfig()
    cfg.artnet_default_ip = "192.168.4.1"
    cfg.artnet_default_fps = 60

    ini = tmp_path / "config.ini"
    cfg.save(ini)

    loaded = AppConfig.load(ini)
    assert loaded.artnet_default_ip == "192.168.4.1"
    assert loaded.artnet_default_fps == 60
    assert loaded.artnet_default_universe == 0


def test_load_missing_file_returns_defaults(tmp_path) -> None:
    missing = tmp_path / "nope.ini"
    cfg = AppConfig.load(missing)
    assert cfg.artnet_default_ip == "127.0.0.1"
    assert cfg.app_name == "zzluxora"


def test_save_creates_valid_ini(tmp_path) -> None:
    cfg = AppConfig()
    ini = tmp_path / "config.ini"
    cfg.save(ini)

    parser = configparser.ConfigParser()
    parser.read(ini)
    assert parser.has_section("artnet")
    assert parser.getint("artnet", "universe") == 0
    assert parser.getint("artnet", "port") == 6454
    assert parser.get("artnet", "default_ip") == "127.0.0.1"
