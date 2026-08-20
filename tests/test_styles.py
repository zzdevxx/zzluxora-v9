"""Tests for zzluxora.ui.styles — GrandMA3 design tokens (DESIGN.md §2)."""
from __future__ import annotations

from zzluxora.ui.styles import COLORS, build_qss


def test_color_tokens_exist() -> None:
    """Token wajib dari DESIGN.md §2."""
    assert COLORS["bg_deep"] == "#000000"
    assert COLORS["bg_base"] == "#0F0F0F"
    assert COLORS["bg_panel"] == "#121215"
    assert COLORS["bg_elevated"] == "#1C1C1E"
    assert COLORS["bg_toolbar"] == "#26282A"
    assert COLORS["text_primary"] == "#FFFFFF"
    assert COLORS["text_secondary"] == "#9A9AA0"
    assert COLORS["accent_blue"] == "#5C96FD"
    assert COLORS["ok_green"] == "#00B300"
    assert COLORS["warn_yellow"] == "#F1C40F"
    assert COLORS["danger_red"] == "#FF3333"
    assert COLORS["magenta"] == "#FF00FF"


def test_qss_contains_dark_background() -> None:
    qss = build_qss()
    assert "#0F0F0F" in qss
    assert "#121215" in qss


def test_qss_contains_accent_blue() -> None:
    qss = build_qss()
    assert "#5C96FD" in qss


def test_qss_styles_main_widgets() -> None:
    qss = build_qss()
    for selector in ("QMainWindow", "QPushButton", "QSlider", "QLineEdit", "QListWidget"):
        assert selector in qss


def test_qss_no_emoji_or_markdown() -> None:
    qss = build_qss()
    assert "**" not in qss
    assert "```" not in qss
