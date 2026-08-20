"""Tests for zzluxora.ui.panels.scenes_panel — scene cards + chase (R3 §10)."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from zzluxora.app import AppContext
from zzluxora.ui.panels.scenes_panel import ScenesPanel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def ctx():
    return AppContext()


def _features() -> dict:
    return {
        "bpm": 100, "rms": 0.3, "spectral_centroid": 2200,
        "mfcc1": -30, "chroma_major_ratio": 0.7, "onset_rate": 1.8,
        "beat_times": [], "duration_s": 16.0,
    }


def test_panel_empty_without_song(qapp, ctx) -> None:
    p = ScenesPanel(ctx)
    assert p.scene_count() == 0
    p.close()


def test_add_scenes_from_features(qapp, ctx) -> None:
    p = ScenesPanel(ctx)
    p.set_features(_features())
    # 16s / 4s per segmen = 4 scenes
    assert p.scene_count() >= 4
    p.close()


def test_scene_card_has_section_label(qapp, ctx) -> None:
    p = ScenesPanel(ctx)
    p.set_features(_features())
    texts = p.card_labels()
    assert any("INTRO" in t or "VERSE" in t or "CHORUS" in t for t in texts)
    p.close()


def test_add_to_chase(qapp, ctx) -> None:
    p = ScenesPanel(ctx)
    p.set_features(_features())
    before = p.chase_cue_count()
    p.add_current_to_chase()
    assert p.chase_cue_count() == before + 1
    p.close()
