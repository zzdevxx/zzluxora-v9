"""Tests for zzluxora.ui.panels.fixture_editor — fixture editor (R1 QLC+)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QPushButton

from zzluxora.app import AppContext
from zzluxora.ui.panels.fixture_editor import FixtureEditor


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_editor_has_name_field(qapp, ctx) -> None:
    e = FixtureEditor(ctx)
    field = e.findChild(QLineEdit, "nameEdit")
    assert field is not None
    e.close()


def test_editor_has_type_selector(qapp, ctx) -> None:
    e = FixtureEditor(ctx)
    combo = e.findChild(QComboBox, "typeCombo")
    assert combo is not None
    assert combo.count() >= 4  # Dimmer, Red, Green, Blue...
    e.close()


def test_editor_save_adds_fixture(qapp, ctx) -> None:
    e = FixtureEditor(ctx)
    e.name_edit.setText("Beam1")
    e.save()
    e.close()
    # fixture tersimpan di ctx
    names = [f.name for f in ctx.fixtures]
    assert "Beam1" in names


def test_editor_type_count_applies(qapp, ctx) -> None:
    e = FixtureEditor(ctx)
    e.name_edit.setText("Strip1")
    e.type_combo.setCurrentIndex(0)  # 8 kanal default
    e.save()
    e.close()
    f = next(f for f in ctx.fixtures if f.name == "Strip1")
    assert len(f.types) == 8
