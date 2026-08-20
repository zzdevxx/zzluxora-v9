"""Tests for zzluxora.ui.panels.settings_panel — settings (R3 §21, R4)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton

from zzluxora.app import AppContext
from zzluxora.ui.panels.settings_panel import SettingsPanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def test_settings_has_ip_field(qapp, ctx) -> None:
    p = SettingsPanel(ctx)
    edit = p.findChild(QLineEdit, "settingsIpEdit")
    assert edit is not None
    assert edit.text() == ctx.cfg.artnet_default_ip
    p.close()


def test_save_persists_to_config(qapp, ctx, tmp_path) -> None:
    p = SettingsPanel(ctx)
    p.ip_edit.setText("10.0.0.5")
    ini = tmp_path / "config.ini"
    p.save(ini)
    from zzluxora.config import AppConfig
    loaded = AppConfig.load(ini)
    assert loaded.artnet_default_ip == "10.0.0.5"
    p.close()


def test_about_dialog(qapp, ctx) -> None:
    from zzluxora.ui.panels.about_panel import AboutDialog
    dlg = AboutDialog(ctx)
    assert "ZZLUXORA" in dlg.windowTitle()
    dlg.close()
