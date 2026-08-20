"""Tests for zzluxora.ui.panels.chase_panel — chase timeline (R1 Function Mgr)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QPushButton

from zzluxora.app import AppContext
from zzluxora.ui.panels.chase_panel import ChasePanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_panel_has_add_remove_buttons(qapp, ctx) -> None:
    p = ChasePanel(ctx)
    assert p.findChild(QPushButton, "addCueBtn") is not None
    assert p.findChild(QPushButton, "removeCueBtn") is not None
    p.close()


def test_add_cue_increments_list(qapp, ctx) -> None:
    p = ChasePanel(ctx)
    before = p.cue_count()
    p.add_cue("Scene A", 500)
    assert p.cue_count() == before + 1
    p.close()


def test_remove_cue_decrements(qapp, ctx) -> None:
    p = ChasePanel(ctx)
    p.add_cue("Scene A", 500)
    p.add_cue("Scene B", 700)
    before = p.cue_count()
    p.remove_cue(0)
    assert p.cue_count() == before - 1
    p.close()


def test_remove_cue_on_empty_noop(qapp, ctx) -> None:
    p = ChasePanel(ctx)
    p.remove_cue(0)
    assert p.cue_count() == 0
    p.close()


def test_direction_selector(qapp, ctx) -> None:
    p = ChasePanel(ctx)
    assert p.direction() in ("forward", "backward", "bounce")
    p.close()
