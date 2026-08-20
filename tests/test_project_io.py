"""Tests for zzluxora.core.project_io — .zlx save/load (R3 §4)."""
from __future__ import annotations

import json

import pytest

from zzluxora.core.models import Chase, Cue, Fixture, Scene, make_par_rgbw_8ch
from zzluxora.core.project_io import (
    DEFAULT_FILENAME,
    ProjectData,
    load_project,
    save_project,
)


def _sample_project() -> ProjectData:
    f = make_par_rgbw_8ch()
    f.address = 1
    scene = Scene(name="Chorus", start_ms=0, end_ms=5000, section="chorus")
    chase = Chase(name="Main Chase", cues=[Cue(scene_id="chorus", hold_ms=700)])
    return ProjectData(
        project_name="MyShow.zlx",
        fixtures=[f],
        scenes=[scene],
        chases=[chase],
        artnet={"target_ip": "192.168.4.1", "universe": 0, "fps": 30},
        version="3.0",
    )


def test_default_filename() -> None:
    assert DEFAULT_FILENAME == "untitled.zlx"


def test_save_load_roundtrip(tmp_path) -> None:
    proj = _sample_project()
    path = tmp_path / "test.zlx"
    save_project(proj, path)

    loaded = load_project(path)
    assert loaded.project_name == "MyShow.zlx"
    assert loaded.version == "3.0"
    assert len(loaded.fixtures) == 1
    assert loaded.fixtures[0].name == "PAR RGBW 8ch"
    assert loaded.fixtures[0].types == ["Dimmer", "Red", "Green", "Blue", "Empty", "Program", "Speed", "Empty"]
    assert len(loaded.scenes) == 1
    assert loaded.scenes[0].name == "Chorus"
    assert len(loaded.chases) == 1
    assert loaded.chases[0].cues[0].hold_ms == 700
    assert loaded.artnet["target_ip"] == "192.168.4.1"
    assert loaded.artnet["universe"] == 0


def test_save_creates_valid_json(tmp_path) -> None:
    proj = _sample_project()
    path = tmp_path / "valid.zlx"
    save_project(proj, path)

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["project_name"] == "MyShow.zlx"
    assert "fixtures" in raw and "chases" in raw and "scenes" in raw


def test_load_missing_file_raises(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_project(tmp_path / "nope.zlx")


def test_load_corrupt_file_raises(tmp_path) -> None:
    bad = tmp_path / "bad.zlx"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_project(bad)


def test_empty_project_ok(tmp_path) -> None:
    proj = ProjectData(project_name="Empty.zlx")
    path = tmp_path / "empty.zlx"
    save_project(proj, path)
    loaded = load_project(path)
    assert loaded.project_name == "Empty.zlx"
    assert loaded.fixtures == [] and loaded.chases == []
