"""Tests for build.py — release helper sanity (M8 Task 8.2)."""
from __future__ import annotations

from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parents[1]


def test_build_script_exists() -> None:
    assert (PKG_ROOT / "build.py").is_file()


def test_build_script_no_splash() -> None:
    """D7 — build harus tanpa splash screen."""
    content = (PKG_ROOT / "build.py").read_text(encoding="utf-8")
    assert "Splash" not in content


def test_build_script_onefile() -> None:
    content = (PKG_ROOT / "build.py").read_text(encoding="utf-8")
    assert "--onefile" in content


def test_build_script_uses_venv() -> None:
    content = (PKG_ROOT / "build.py").read_text(encoding="utf-8")
    assert ".venv" in content or "venv" in content
