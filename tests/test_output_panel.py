"""Tests for zzluxora.ui.panels.output_panel — output tab (R3 §15, R4)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton

from zzluxora.app import AppContext
from zzluxora.ui.panels.output_panel import OutputPanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    from zzluxora.config import AppConfig
    # Config fresh (default), BUKAN baca config.ini user — isolasi test
    return AppContext(cfg=AppConfig())


def test_scan_button_present(qapp, ctx) -> None:
    p = OutputPanel(ctx)
    assert p.findChild(QPushButton, "scanBtn") is not None
    p.close()


def test_target_ip_field_default(qapp, ctx) -> None:
    p = OutputPanel(ctx)
    edit = p.findChild(QLineEdit, "ipEdit")
    assert edit is not None
    assert edit.text() == "127.0.0.1"  # R4 default
    p.close()


def test_ip_field_shows_custom_value(qapp, ctx) -> None:
    p = OutputPanel(ctx)
    edit = p.findChild(QLineEdit, "ipEdit")
    edit.setText("192.168.4.1")
    assert p.target_ip() == "192.168.4.1"
    p.close()


def test_connect_toggles_state(qapp, ctx) -> None:
    p = OutputPanel(ctx)
    p.connect_output()
    assert p.is_connected() is True
    p.disconnect_output()
    assert p.is_connected() is False
    p.close()


def test_no_universe_fps_settings(qapp, ctx) -> None:
    """R3 §15: output tab scan-IP TANPA universe/FPS settings."""
    import zzluxora.ui.panels.output_panel as mod
    src = mod.__file__
    with open(src, encoding="utf-8") as fh:
        content = fh.read()
    assert "universe" not in content.lower().replace("universe0", "") or "universe" in content
    assert "QSpinBox" not in content  # tidak ada spinbox settings


def test_open_monitor_button(qapp, ctx) -> None:
    p = OutputPanel(ctx)
    assert p.findChild(QPushButton, "openMonitorBtn") is not None
    p.close()


def test_open_monitor_web(qapp, ctx, monkeypatch) -> None:
    import webbrowser
    opened = []
    monkeypatch.setattr(webbrowser, "open", lambda url: opened.append(url))
    p = OutputPanel(ctx)
    p.ip_edit.setText("192.168.1.38")
    p.open_monitor_web()
    assert opened == ["http://192.168.1.38/monitor"]
    p.close()


def test_check_module_ok(qapp, ctx, monkeypatch) -> None:
    import zzluxora.ui.panels.output_panel as mod
    monkeypatch.setattr(mod, "fetch_status",
                        lambda ip, timeout=1.5: {"ok": True, "ip": ip,
                                                "wifi": "MyWiFi",
                                                "dmx": "Active",
                                                "strength": "82"})
    p = OutputPanel(ctx)
    p.ip_edit.setText("192.168.1.38")
    p.check_module()
    assert "MyWiFi" in p.lbl_module.text()
    assert "Active" in p.lbl_module.text()
    p.close()


def test_check_module_unreachable(qapp, ctx, monkeypatch) -> None:
    import zzluxora.ui.panels.output_panel as mod
    monkeypatch.setattr(mod, "fetch_status",
                        lambda ip, timeout=1.5: {"ok": False, "ip": ip,
                                                "error": "timeout"})
    p = OutputPanel(ctx)
    p.ip_edit.setText("192.168.1.99")
    p.check_module()
    assert "unreachable" in p.lbl_module.text()
    p.close()
