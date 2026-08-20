"""Tests for zzluxora.ui.panels.analyze_panel — state machine (R3 §9)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QPushButton

from zzluxora.app import AppContext
from zzluxora.ui.panels.analyze_panel import AnalyzePanel

import zzluxora.ui.panels.analyze_panel as ap_mod


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def _btn(p, name: str) -> QPushButton:
    b = p.findChild(QPushButton, name)
    assert b is not None, f"button {name} missing"
    return b


def test_initial_state_load_enabled_others_disabled(qapp, ctx) -> None:
    p = AnalyzePanel(ctx)
    assert _btn(p, "loadBtn").isEnabled()
    assert not _btn(p, "analyzeBtn").isEnabled()
    assert not _btn(p, "removeBtn").isEnabled()
    assert not _btn(p, "exportBtn").isEnabled()
    p.close()


def test_select_song_enables_analyze_remove(qapp, ctx, tmp_path) -> None:
    p = AnalyzePanel(ctx)
    f = tmp_path / "song.wav"
    f.write_bytes(b"RIFF")  # dummy — hanya untuk state test (button state)
    p.set_song(str(f))
    assert _btn(p, "analyzeBtn").isEnabled()
    assert _btn(p, "removeBtn").isEnabled()
    assert not _btn(p, "exportBtn").isEnabled()
    p.close()


def test_remove_clears_song(qapp, ctx, tmp_path) -> None:
    p = AnalyzePanel(ctx)
    f = tmp_path / "song.wav"
    f.write_bytes(b"RIFF")
    p.set_song(str(f))
    p.remove_song()
    assert p.song_path is None
    assert not _btn(p, "analyzeBtn").isEnabled()
    p.close()


def test_analyze_starts_thread(qapp, ctx, tmp_path, monkeypatch) -> None:
    p = AnalyzePanel(ctx)
    f = tmp_path / "song.wav"
    f.write_bytes(b"RIFF")

    started = []

    class FakeThread(QThread):
        def start(self, *a, **kw):
            started.append(True)
            # simulate langsung selesai
            p._on_analyze_finished({})

    monkeypatch.setattr(ap_mod, "QThread", FakeThread)

    p.set_song(str(f))
    p.start_analyze()
    assert started == [True]
    assert _btn(p, "exportBtn").isEnabled()
    p.close()
