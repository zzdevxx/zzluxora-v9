"""Tests for zzluxora.ui.panels.mixer_panel — 513 fader mixer (R3 §13)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QSlider

from zzluxora.app import AppContext
from zzluxora.ui.panels.mixer_panel import MixerPanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_mixer_has_512_sliders(qapp, ctx) -> None:
    p = MixerPanel(ctx)
    assert p.slider_count() == 512
    p.close()


def test_slider_binds_to_mixer_state(qapp, ctx) -> None:
    p = MixerPanel(ctx)
    slider = p.slider_at(0)
    assert slider.value() == ctx.mixer.channels[0]
    p.close()


def test_move_slider_updates_mixer(qapp, ctx) -> None:
    p = MixerPanel(ctx)
    p.show()
    qapp.processEvents()
    slider = p.slider_at(0)
    slider.setValue(128)
    qapp.processEvents()
    assert ctx.mixer.channels[0] == 128
    p.close()


def test_master_slider_present(qapp, ctx) -> None:
    p = MixerPanel(ctx)
    assert p.master_slider() is not None
    p.close()
