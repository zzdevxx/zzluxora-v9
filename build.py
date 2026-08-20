#!/usr/bin/env python
"""Build script — PyInstaller one-file EXE (M8 Task 8.2).

Usage:
    python build.py            # build (Debug window)
    python build.py --noconsole # build tanpa console
    python build.py --clean     # bersihkan build/ + dist/ dulu

Hasil: dist/ZZLUXORA.exe — satu file, tanpa splash (D7).
Dependencies penting yang ikut: PySide6, librosa, numpy, scipy, soundfile.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
VENV_PY = ROOT.parent / "SCRIPT" / ".venv" / "Scripts" / "python.exe"

APP_NAME = "ZZLUXORA"
MAIN_SCRIPT = str(SRC / "zzluxora" / "__main__.py")


def venv_python() -> str:
    if VENV_PY.is_file():
        return str(VENV_PY)
    return sys.executable


def main() -> int:
    clean = "--clean" in sys.argv
    noconsole = "--noconsole" in sys.argv

    if clean:
        for d in ("build", "dist"):
            p = ROOT / d
            if p.exists():
                shutil.rmtree(p)
        spec = ROOT / f"{APP_NAME}.spec"
        if spec.exists():
            spec.unlink()
        print(f"[build] cleaned build/, dist/ ({APP_NAME}.spec)")

    cmd = [
        venv_python(), "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name", APP_NAME,
        "--paths", str(SRC),
        "--hidden-import", "soundfile",
        "--hidden-import", "librosa",
        "--hidden-import", "scipy",
        "--hidden-import", "numpy",
    ]
    if noconsole:
        cmd.append("--noconsole")
    cmd.append(MAIN_SCRIPT)

    print(f"[build] running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode == 0:
        exe = ROOT / "dist" / f"{APP_NAME}.exe"
        print(f"[build] DONE -> {exe}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
