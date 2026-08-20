"""Tests for zzluxora.ui.panels.address_panel — Address tab (R3 §8)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QPushButton

from zzluxora.app import AppContext
from zzluxora.ui.panels.address_panel import AddressPanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_panel_has_autopatch_button(qapp, ctx) -> None:
    p = AddressPanel(ctx)
    btn = p.findChild(QPushButton, "autoPatchBtn")
    assert btn is not None
    p.close()


def test_panel_has_clear_all_button(qapp, ctx) -> None:
    p = AddressPanel(ctx)
    btn = p.findChild(QPushButton, "clearAllBtn")
    assert btn is not None
    p.close()


def test_panel_grid_24_cols(qapp, ctx) -> None:
    p = AddressPanel(ctx)
    assert p.grid.cols == 24
    p.close()


def test_auto_patch_places_fixtures(qapp, ctx) -> None:
    # fixture bawaan (default v7/v9: 4x PAR RGBW 8-kanal)
    p = AddressPanel(ctx)
    p.grid.clear_all()
    assert len(p.grid.fixtures()) == 0
    p.auto_patch()
    assert len(p.grid.fixtures()) > 0
    p.close()


def test_clear_all_empty_grid(qapp, ctx) -> None:
    p = AddressPanel(ctx)
    p.auto_patch()
    p.clear_all()
    assert len(p.grid.fixtures()) == 0
    p.close()
