"""Live Art-Net test — kirim DMX ke modul (fader 1-8 check).

Usage:
    python tools/live_test.py 192.168.1.38          # test channel 1-8
    python tools/live_test.py 192.168.1.38 --cycle  # nyalakan berurutan 1-8
    python tools/live_test.py 192.168.1.38 --off    # semua 0 (blackout)

Channel 1-8 (fixture PAR1 8-kanal): 1=Dimmer, 2=Red, 3=Green, 4=Blue,
5=Empty, 6=Program, 7=Speed, 8=Empty (R2 8-kanal).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zzluxora.core.artnet_sender import ArtNetSender

UNIVERSE = 0  # R4: universe wajib 0


def set_channel(sender: ArtNetSender, ch: int, value: int = 255) -> None:
    dmx = [0] * 512
    dmx[ch - 1] = value
    sender.send(dmx)
    print(f"  ch{ch} = {value}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    ip = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "static"

    sender = ArtNetSender(target_ip=ip, port=6454, universe=UNIVERSE)

    if mode == "--off":
        sender.blackout()
        print(f"[OK] blackout semua channel -> {ip}")
        sender.close()
        return 0

    if mode == "--cycle":
        print(f"[*] Cycle channel 1-8 -> {ip} (universe {UNIVERSE})")
        for ch in range(1, 9):
            set_channel(sender, ch)
            time.sleep(0.8)
        sender.blackout()
        print("[OK] cycle selesai, blackout")
        sender.close()
        return 0

    # static: nyalakan ch1-8 dengan nilai (default 255)
    print(f"[*] Test channel 1-8 -> {ip} (universe {UNIVERSE})")
    for ch in range(1, 9):
        set_channel(sender, ch)
    time.sleep(2)
    sender.blackout()
    print("[OK] test selesai, blackout")
    sender.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
