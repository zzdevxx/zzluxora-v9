"""Tests for zzluxora.ui.main_window — shell layout (R3 §3, §4)."""
from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from zzluxora.app import AppContext
from zzluxora.ui.main_window import MainWindow

# package root = C:\ANDREAS\SCRIPT3
PKG_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_window_title(qapp, ctx) -> None:
    w = MainWindow(ctx)
    assert w.windowTitle() == "ZZLUXORA"
    w.close()


def test_has_menubar(qapp, ctx) -> None:
    w = MainWindow(ctx)
    assert w.menuBar() is not None
    w.close()


def test_menubar_actions(qapp, ctx) -> None:
    w = MainWindow(ctx)
    titles = [a.text() for a in w.menuBar().actions()]
    assert any("File" in t for t in titles)
    assert any("View" in t for t in titles)
    assert any("Help" in t for t in titles)
    w.close()


def test_header_project_label(qapp, ctx) -> None:
    w = MainWindow(ctx)
    assert w.ui_project_label.text() == "untitled.zlx"
    w.close()


def test_artnet_pill(qapp, ctx) -> None:
    w = MainWindow(ctx)
    assert w.ui_artnet_pill.text() == "ART-NET"
    w.close()


def test_play_pause_toggle(qapp, ctx) -> None:
    w = MainWindow(ctx)
    assert w.ui_play_pause.isCheckable()
    assert w.ui_play_pause.text() == "PLAY"
    w.close()


def test_blackout_button(qapp, ctx) -> None:
    w = MainWindow(ctx)
    assert w.ui_blackout.isCheckable()
    w.close()


def test_sidebar_five_items(qapp, ctx) -> None:
    w = MainWindow(ctx)
    items = [w.ui_sidebar.item(i).text() for i in range(w.ui_sidebar.count())]
    assert items == ["Program", "Fixture List", "Fixture Editor",
                     "Settings", "About"]
    w.close()


def test_sidebar_collapsed_default(qapp, ctx) -> None:
    """R3 §103: sidebar tertutup secara default."""
    w = MainWindow(ctx)
    w.show()
    qapp.processEvents()
    assert w.ui_sidebar.isHidden()
    w.close()


def test_hamburger_button_exists(qapp, ctx) -> None:
    """R3 §98: hamburger di pojok kiri atas."""
    w = MainWindow(ctx)
    assert w.ui_hamburger is not None
    assert w.ui_hamburger.toolTip() == "Toggle Sidebar"
    w.close()


def test_sidebar_toggle_requires_project(qapp, ctx) -> None:
    """R3 §107: sidebar baru bisa dibuka setelah project di-load."""
    w = MainWindow(ctx)
    w.show()
    qapp.processEvents()
    w.toggle_sidebar()
    qapp.processEvents()
    assert w.ui_sidebar.isHidden()  # tanpa project → tidak bisa buka
    w.close()


def test_sidebar_opens_after_project(qapp, ctx, tmp_path) -> None:
    w = MainWindow(ctx)
    w.show()
    qapp.processEvents()
    ctx.set_project(str(tmp_path / "proj.zlx"))
    w.toggle_sidebar()
    qapp.processEvents()
    assert not w.ui_sidebar.isHidden()
    w.close()


def test_sidebar_maps_to_main_tabs(qapp, ctx) -> None:
    """DQ1: sidebar row -> tab utama QLC+ (5 section)."""
    w = MainWindow(ctx)
    assert w.ui_main_tabs.count() == 5
    w._show_main_tab(2)
    assert w.ui_main_tabs.currentIndex() == 2  # Program
    w.close()
def test_toggle_sidebar(qapp, ctx) -> None:
    w = MainWindow(ctx)
    w.show()
    qapp.processEvents()
    # toggle butuh project ter-load (R3 §107)
    ctx.set_project("proj.zlx")
    qapp.processEvents()
    # default collapsed → buka dulu
    assert w.ui_sidebar.isHidden()
    w.toggle_sidebar()
    qapp.processEvents()
    assert not w.ui_sidebar.isHidden()
    w.toggle_sidebar()
    qapp.processEvents()
    assert w.ui_sidebar.isHidden()
    w.toggle_sidebar()
    qapp.processEvents()
    assert not w.ui_sidebar.isHidden()
    w.close()


def test_no_splash_screen() -> None:
    """D7 — no splash screen. Regression guard di __main__."""
    src = (PKG_ROOT / "src" / "zzluxora" / "__main__.py").read_text(encoding="utf-8")
    assert "Splash" not in src
