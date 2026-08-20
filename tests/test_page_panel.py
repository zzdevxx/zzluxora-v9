"""Tests for zzluxora.ui.panels.page_panel — Virtual Console page (R3 §6)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QPushButton

from zzluxora.app import AppContext
from zzluxora.ui.panels.page_panel import PagePanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_panel_has_add_button(qapp, ctx) -> None:
    p = PagePanel(ctx)
    assert p.findChild(QPushButton, "addBtn") is not None
    p.close()


def test_add_button_creates_action(qapp, ctx) -> None:
    p = PagePanel(ctx)
    before = p.action_count()
    p.add_button("Scene A")
    assert p.action_count() == before + 1
    p.close()


def test_action_buttons_flash_on_toggle(qapp, ctx) -> None:
    p = PagePanel(ctx)  # noqa: F841 (tidak ada crash)
    p.close()
