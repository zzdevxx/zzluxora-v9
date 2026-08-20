"""Tests for module monitor — fetch status dari modul (firmware /status)."""
from __future__ import annotations

import json

import pytest

from zzluxora.services.module_monitor import fetch_status


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self) -> bytes:
        return self._payload


def test_fetch_status_parses_json(monkeypatch) -> None:
    payload = json.dumps({
        "ip": "192.168.1.38", "wifi": "MyWiFi",
        "status": "Connected", "strength": "82",
        "dmx": "Active",
    }).encode("utf-8")

    def fake_urlopen(url, timeout=2.0):
        assert url == "http://192.168.1.38/status"
        assert timeout == 2.0
        return FakeResponse(payload)

    monkeypatch.setattr("zzluxora.services.module_monitor.urllib.request.urlopen",
                        fake_urlopen)
    result = fetch_status("192.168.1.38")
    assert result["ok"] is True
    assert result["dmx"] == "Active"
    assert result["ip"] == "192.168.1.38"


def test_fetch_status_timeout_returns_error(monkeypatch) -> None:
    def fake_urlopen(url, timeout=2.0):
        raise TimeoutError("timed out")

    monkeypatch.setattr("zzluxora.services.module_monitor.urllib.request.urlopen",
                        fake_urlopen)
    result = fetch_status("192.168.1.38", timeout=1.0)
    assert result["ok"] is False
    assert "error" in result
    assert result["ip"] == "192.168.1.38"


def test_fetch_status_bad_json(monkeypatch) -> None:
    def fake_urlopen(url, timeout=2.0):
        return FakeResponse(b"not json")

    monkeypatch.setattr("zzluxora.services.module_monitor.urllib.request.urlopen",
                        fake_urlopen)
    result = fetch_status("192.168.1.38")
    assert result["ok"] is False


def test_fetch_status_unreachable(monkeypatch) -> None:
    def fake_urlopen(url, timeout=2.0):
        raise OSError("no route to host")

    monkeypatch.setattr("zzluxora.services.module_monitor.urllib.request.urlopen",
                        fake_urlopen)
    result = fetch_status("192.168.1.99")
    assert result["ok"] is False
    assert "no route" in result["error"]
