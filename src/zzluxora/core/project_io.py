"""Project IO — .zlx JSON save/load (R3 §4-5).

Format: JSON, backward compatible with v3.0+ (see PRD §5 / v7 README).
Schema: {version, project_name, fixtures[], scenes[], chases[], artnet{},
        created_at, updated_at}
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from zzluxora.core.models import Chase, Cue, DRGBW, Fixture, Scene

DEFAULT_FILENAME = "untitled.zlx"
FORMAT_VERSION = "3.0"


@dataclass
class ProjectData:
    project_name: str = DEFAULT_FILENAME
    fixtures: list[Fixture] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    chases: list[Chase] = field(default_factory=list)
    artnet: dict[str, Any] = field(
        default_factory=lambda: {"target_ip": "127.0.0.1", "universe": 0, "fps": 30}
    )
    version: str = FORMAT_VERSION
    created_at: str = ""
    updated_at: str = ""


# ----------------------------------------------------------------------
# Scene values: {fixture_name: [dimmer, r, g, b, w]} compact form
# ----------------------------------------------------------------------
def _values_to_dict(scene: Scene) -> dict[str, list[int]]:
    return {name: list(v.as_tuple()) for name, v in scene.values.items()}


def _values_from_dict(data: dict[str, list[int]]) -> dict[str, DRGBW]:
    return {name: DRGBW(*vals) for name, vals in data.items()}


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def save_project(project: ProjectData, path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    if not project.created_at:
        project.created_at = now
    project.updated_at = now

    payload: dict[str, Any] = {
        "version": project.version,
        "project_name": project.project_name,
        "fixtures": [f.to_dict() for f in project.fixtures],
        "scenes": [
            {
                "name": s.name,
                "start_ms": s.start_ms,
                "end_ms": s.end_ms,
                "section": s.section,
                "hue": s.hue,
                "values": _values_to_dict(s),
            }
            for s in project.scenes
        ],
        "chases": [
            {
                "name": c.name,
                "direction": c.direction,
                "loop": c.loop,
                "fps": c.fps,
                "cues": [
                    {
                        "scene_id": cue.scene_id,
                        "hold_ms": cue.hold_ms,
                        "fade_in_ms": cue.fade_in_ms,
                        "fade_out_ms": cue.fade_out_ms,
                    }
                    for cue in c.cues
                ],
            }
            for c in project.chases
        ],
        "artnet": project.artnet,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_project(path: Path | str) -> ProjectData:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Project file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Corrupt .zlx file: {path} — {exc}") from exc

    proj = ProjectData(project_name=str(raw.get("project_name", DEFAULT_FILENAME)))
    proj.version = str(raw.get("version", FORMAT_VERSION))
    proj.created_at = str(raw.get("created_at", ""))
    proj.updated_at = str(raw.get("updated_at", ""))
    proj.artnet = dict(raw.get("artnet", {})) or proj.artnet

    proj.fixtures = [Fixture.from_dict(f) for f in raw.get("fixtures", [])]
    proj.scenes = [
        Scene(
            name=str(s.get("name", "Scene")),
            start_ms=int(s.get("start_ms", 0)),
            end_ms=int(s.get("end_ms", 0)),
            section=str(s.get("section", "verse")),
            hue=float(s.get("hue", 0.0)),
            values=_values_from_dict(s.get("values", {})),
        )
        for s in raw.get("scenes", [])
    ]
    proj.chases = [
        Chase(
            name=str(c.get("name", "Chase")),
            direction=str(c.get("direction", "forward")),
            loop=bool(c.get("loop", True)),
            fps=int(c.get("fps", 30)),
            cues=[
                Cue(
                    scene_id=str(cue.get("scene_id", "")),
                    hold_ms=int(cue.get("hold_ms", 500)),
                    fade_in_ms=int(cue.get("fade_in_ms", 100)),
                    fade_out_ms=int(cue.get("fade_out_ms", 100)),
                )
                for cue in c.get("cues", [])
            ],
        )
        for c in raw.get("chases", [])
    ]
    return proj
