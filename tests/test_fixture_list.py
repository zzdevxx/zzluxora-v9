"""Tests for zzluxora.ui.panels.fixture_list — fixture list (R1 QLC+ fixture mgr)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from zzluxora.app import AppContext
from zzluxora.ui.panels.fixture_list import FixtureListPanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_list_has_default_fixtures(qapp, ctx) -> None:
    p = FixtureListPanel(ctx)
    assert p.count() == 4  # 4x PAR default
    p.close()


def test_add_fixture(qapp, ctx) -> None:
    p = FixtureListPanel(ctx)
    before = p.count()
    p.add_fixture("PAR5", ["Dimmer", "Red", "Green", "Blue"])
    assert p.count() == before + 1
    p.close()


def test_remove_fixture(qapp, ctx) -> None:
    p = FixtureListPanel(ctx)
    before = p.count()
    p.list.setCurrentRow(0)
    p.remove_selected()
    assert p.count() == before - 1
    p.close()


def test_item_shows_channel_count(qapp, ctx) -> None:
    p = FixtureListPanel(ctx)
    item = p.item(0)
    assert "8ch" in item.text()  # PAR RGBW 8-kanal
    p.close()
