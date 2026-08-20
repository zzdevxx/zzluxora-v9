"""Tests for zzluxora.ui.widgets.address_grid — DMX address grid (R3 §8)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from zzluxora.core.models import Fixture
from zzluxora.ui.widgets.address_grid import AddressGrid


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_grid_24_cells_per_row(qapp) -> None:
    g = AddressGrid(rows=3)
    assert g.cols == 24  # R3 §8: max 24 kotak/baris
    assert g.row_count == 3


def test_empty_cell_shows_address_number(qapp) -> None:
    g = AddressGrid(rows=2)
    cell = g.cell_widget(0, 0)
    assert cell.text() == "1"  # channel 1 (pojok kiri atas)


def test_set_fixture_marks_cell(qapp) -> None:
    g = AddressGrid(rows=2)
    f = Fixture(name="PAR1", types=["Dimmer", "Red", "Green", "Blue"])
    g.set_fixture(channel=1, fixture=f)
    cell = g.cell_widget(0, 0)
    assert "PAR1" in cell.text()
    assert "1" in cell.text()  # address tetap tampil


def test_set_fixture_spans_channels(qapp) -> None:
    g = AddressGrid(rows=2)
    f = Fixture(name="PAR1", types=["Dimmer", "Red", "Green", "Blue"])
    g.set_fixture(channel=1, fixture=f)
    # 4 channel → PAR1 di 1..4, sel 2..4 berisi label tanpa angka
    cell2 = g.cell_widget(0, 1)
    assert "PAR1" in cell2.text()
    cell5 = g.cell_widget(0, 4)
    assert cell5.text() == "5"  # kosong lagi


def test_clear_all(qapp) -> None:
    g = AddressGrid(rows=2)
    f = Fixture(name="PAR1", types=["Dimmer", "Red"])
    g.set_fixture(channel=1, fixture=f)
    g.clear_all()
    cell = g.cell_widget(0, 0)
    assert cell.text() == "1"


def test_click_empty_cell_selects(qapp) -> None:
    g = AddressGrid(rows=1)
    g.show()
    qapp.processEvents()
    cell = g.cell_widget(0, 0)
    QTest.mouseClick(cell, Qt.LeftButton)
    qapp.processEvents()
    assert g.selected_channel == 1
    g.close()
