"""Tests for zzluxora.ui.panels.preview_panel — draggable fixtures (R1 Preview)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from zzluxora.app import AppContext
from zzluxora.ui.panels.preview_panel import PreviewPanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_preview_has_fixture_badges(qapp, ctx) -> None:
    p = PreviewPanel(ctx)
    assert p.fixture_count() >= 4  # 4x PAR default
    p.close()


def test_drag_moves_fixture(qapp, ctx) -> None:
    p = PreviewPanel(ctx)
    p.show()
    qapp.processEvents()
    f = p.fixture_at(0)
    before = f.pos()
    QTest.mousePress(f, Qt.LeftButton, pos=QPoint(5, 5))
    QTest.mouseMove(f, QPoint(30, 40), delay=10)
    QTest.mouseRelease(f, Qt.LeftButton, pos=QPoint(30, 40))
    qapp.processEvents()
    after = f.pos()
    assert after != before
    p.close()
