"""Output Panel — scan IP + connect (R3 §15, R4).

  - Scan IP ala QLC+ (button scan jaringan lokal)
  - Target IP field (default 127.0.0.1 dari config — R4)
  - **TANPA universe/FPS settings** (R3 §15 literal: hanya scan IP + save)
  - CONNECT/DISCONNECT toggle → ArtNetService (core M4)
"""
from __future__ import annotations

import socket

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.services.module_monitor import fetch_status
from zzluxora.ui.styles import COLORS


def scan_local_ips() -> list[str]:
    """Scan IP lokal ala QLC+ (hostname + broadcast discovery)."""
    ips: list[str] = []
    try:
        hostname = socket.gethostname()
        for info in socket.gethostbyname_ex(hostname)[2]:
            if info not in ips:
                ips.append(info)
    except OSError:
        pass
    if "127.0.0.1" not in ips:
        ips.insert(0, "127.0.0.1")
    return ips


class OutputPanel(QWidget):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self._connected = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        lay.addWidget(QLabel("ART-NET OUTPUT"))

        # ── IP + Scan ──────────────────────────────────────────────────
        row = QHBoxLayout()
        row.addWidget(QLabel("Target IP:"))
        self.ip_edit = QLineEdit(self.ctx.cfg.artnet_default_ip)
        self.ip_edit.setObjectName("ipEdit")
        self.ip_edit.setFixedWidth(200)
        row.addWidget(self.ip_edit)

        self.btn_scan = QPushButton("SCAN")
        self.btn_scan.setObjectName("scanBtn")
        self.btn_scan.clicked.connect(self.scan_ip)
        row.addWidget(self.btn_scan)
        row.addStretch(1)
        lay.addLayout(row)

        # ── Connect / Disconnect ───────────────────────────────────────
        self.btn_connect = QPushButton("CONNECT")
        self.btn_connect.setObjectName("connectBtn")
        self.btn_connect.clicked.connect(self.toggle_connect)
        lay.addWidget(self.btn_connect)

        self.lbl_status = QLabel("Status: disconnected")
        self.lbl_status.setStyleSheet(f"color: {COLORS['text_secondary']};")
        lay.addWidget(self.lbl_status)

        # ── Module monitor (firmware /status, L473-488) ────────────────
        mon = QHBoxLayout()
        self.lbl_module = QLabel("Module: not checked")
        self.lbl_module.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 9pt;")
        mon.addWidget(self.lbl_module)
        mon.addStretch(1)
        self.btn_open_monitor = QPushButton("OPEN MONITOR")
        self.btn_open_monitor.setObjectName("openMonitorBtn")
        self.btn_open_monitor.clicked.connect(self.open_monitor_web)
        mon.addWidget(self.btn_open_monitor)
        lay.addLayout(mon)
        lay.addStretch(1)

        # Auto-refresh status modul tiap 2 detik
        self._mon_timer = QTimer(self)
        self._mon_timer.setInterval(2000)
        self._mon_timer.timeout.connect(self.check_module)
        self._mon_timer.start()

    # ── API ───────────────────────────────────────────────────────────
    def target_ip(self) -> str:
        return self.ip_edit.text().strip()

    def is_connected(self) -> bool:
        return self._connected

    def scan_ip(self) -> None:
        ips = scan_local_ips()
        if ips and not self.ip_edit.text().strip():
            self.ip_edit.setText(ips[0])

    def toggle_connect(self) -> None:
        if self._connected:
            self.disconnect_output()
        else:
            self.connect_output()

    def connect_output(self) -> None:
        ip = self.target_ip()
        self.ctx.artnet.sender.target_ip = ip
        self.ctx.cfg.artnet_default_ip = ip  # simpan agar persist (R3 §21)
        self.ctx.artnet.connect()
        self._connected = True
        self.btn_connect.setText("DISCONNECT")
        self.lbl_status.setText(f"Status: connected to {ip}")

    def disconnect_output(self) -> None:
        self.ctx.artnet.disconnect()
        self._connected = False
        self.btn_connect.setText("CONNECT")
        self.lbl_status.setText("Status: disconnected")

    def check_module(self) -> None:
        """Fetch /status dari modul (firmware L473) — non-blocking UI."""
        ip = self.target_ip()
        if not ip:
            self.lbl_module.setText("Module: no IP")
            return
        try:
            result = fetch_status(ip, timeout=1.5)
        except Exception:
            result = {"ok": False, "ip": ip, "error": "exception"}
        if result.get("ok"):
            dmx = result.get("dmx", "?")
            strength = result.get("strength", "?")
            color = COLORS["ok_green"] if dmx == "Active" else COLORS["warn_yellow"]
            self.lbl_module.setStyleSheet(
                f"color: {color}; font-size: 9pt;"
            )
            self.lbl_module.setText(
                f"Module: {result.get('wifi', '?')} | DMX: {dmx} | {strength}"
            )
        else:
            self.lbl_module.setStyleSheet(
                f"color: {COLORS['danger_red']}; font-size: 9pt;"
            )
            self.lbl_module.setText(f"Module: unreachable ({result.get('error', '?')})")

    def open_monitor_web(self) -> None:
        """Buka halaman monitoring modul di browser (firmware /monitor)."""
        import webbrowser
        ip = self.target_ip()
        if ip:
            webbrowser.open(f"http://{ip}/monitor")
