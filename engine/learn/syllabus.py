"""Load syllabus.yaml into simple objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from learn import paths


@dataclass
class Module:
    id: str
    title: str
    track: str
    priority: str
    requires: list[str]
    requires_any: list[str]
    topics: list[str]
    learning_outcomes: list[str]
    planned_problems: int
    project: str | None
    external: bool
    order: int

    @property
    def dir_name(self) -> str:
        return f"{self.id}-{paths.slugify(self.title)}"

    @property
    def content_path(self) -> Path:
        return paths.content_dir() / self.track / self.dir_name

    @property
    def chapter_path(self) -> Path:
        return self.content_path / "chapter.md"


@dataclass
class Track:
    id: str
    title: str
    description: str
    capstone: str | None
    modules: list[Module] = field(default_factory=list)


@dataclass
class Syllabus:
    meta: dict
    tracks: list[Track]

    def track(self, track_id: str) -> Track:
        for t in self.tracks:
            if t.id == track_id:
                return t
        raise KeyError(f"No track named '{track_id}'. Tracks: {', '.join(self.track_ids())}")

    def track_ids(self) -> list[str]:
        return [t.id for t in self.tracks]

    def modules(self) -> list[Module]:
        return [m for t in self.tracks for m in t.modules]

    def module(self, module_id: str) -> Module:
        for m in self.modules():
            if m.id == module_id:
                return m
        raise KeyError(f"No module named '{module_id}'. Try: learn syllabus")


@lru_cache(maxsize=1)
def load() -> Syllabus:
    data = yaml.safe_load(paths.syllabus_path().read_text())
    tracks: list[Track] = []
    order = 0
    for t in data["tracks"]:
        track = Track(
            id=t["id"],
            title=t["title"],
            description=t.get("description", ""),
            capstone=t.get("capstone"),
        )
        for m in t["modules"]:
            track.modules.append(
                Module(
                    id=m["id"],
                    title=m["title"],
                    track=t["id"],
                    priority=m.get("priority", "essential"),
                    requires=list(m.get("requires") or []),
                    requires_any=list(m.get("requires_any") or []),
                    topics=list(m.get("topics") or []),
                    learning_outcomes=list(m.get("learning_outcomes") or []),
                    planned_problems=int(m.get("problems", 0)),
                    project=m.get("project"),
                    external=bool(m.get("external", False)),
                    order=order,
                )
            )
            order += 1
        tracks.append(track)
    return Syllabus(meta=data.get("meta", {}), tracks=tracks)
