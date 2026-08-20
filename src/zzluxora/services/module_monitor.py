"""Module Monitor — status modul Art-Net (firmware /status endpoint).

Firmware artnet_dmx_final.ino (/status, L473-488):
  GET http://<ip>/status  →  JSON {ip, wifi, status, strength, dmx}
    dmx: "Active" (<1s), "No Signal" (<10s), "Loss Signal"
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any


def fetch_status(ip: str, timeout: float = 2.0) -> dict[str, Any]:
    """Fetch /status dari modul. Selalu return dict (tidak raise)."""
    url = f"http://{ip}/status"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        data["ok"] = True
        data["ip"] = ip
        return data
    except TimeoutError:
        return {"ok": False, "ip": ip, "error": "timeout"}
    except Exception as exc:  # OSError, json.JSONDecodeError, dll
        return {"ok": False, "ip": ip, "error": str(exc)}
