"""Discover problems and read their files.

Problem folder layout (inside a module folder):

    problems/p001-some-slug/
        problem.toml      metadata (id, title, tier, kind, topics, difficulty, minutes)
        problem.md        the statement
        starter.py        code you start from        (kind = code)
        test_solution.py  pytest tests that import from solution.py (kind = code)
        reference.py      a correct solution, used by `learn validate`
        expected.txt      the correct answer          (kind = trace)
        answer.md         a model answer              (kind = explain)
        hints.md          "## Hint 1", "## Hint 2", ... sections
        solution.md       full walkthrough
        mistakes.md       common mistakes
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from learn import paths

TIERS = ["drill", "applied", "deep", "challenge"]
KINDS = ["code", "trace", "explain"]
TIER_DIFFICULTY = {"drill": 800, "applied": 1100, "deep": 1400, "challenge": 1700}
TIER_MINUTES = {"drill": 10, "applied": 20, "deep": 25, "challenge": 40}


@dataclass
class Problem:
    id: str
    title: str
    tier: str
    kind: str
    topics: list[str]
    difficulty: int
    minutes: int
    path: Path
    assessment: str | None = None
    requires: list[str] = field(default_factory=list)

    @property
    def module_id(self) -> str:
        return self.id.rsplit(".", 1)[0]

    @property
    def track(self) -> str:
        return self.id.split(".", 1)[0]

    @property
    def short(self) -> str:
        return self.id.rsplit(".", 1)[1]

    def file(self, name: str) -> Path:
        return self.path / name

    def read(self, name: str) -> str:
        f = self.file(name)
        return f.read_text(encoding="utf-8") if f.exists() else ""

    def hints(self) -> list[str]:
        return split_hints(self.read("hints.md"))

    def work_path(self) -> Path:
        return paths.work_dir() / self.track / self.module_id / self.path.name


def split_hints(text: str) -> list[str]:
    parts = re.split(r"^##\s+Hint\b.*$", text, flags=re.MULTILINE)
    return [p.strip() for p in parts[1:] if p.strip()]


def load_problem(toml_path: Path) -> Problem:
    with toml_path.open("rb") as fh:
        meta = tomllib.load(fh)
    tier = meta.get("tier", "drill")
    return Problem(
        id=meta["id"],
        title=meta.get("title", toml_path.parent.name),
        tier=tier,
        kind=meta.get("kind", "code"),
        topics=list(meta.get("topics", [])),
        difficulty=int(meta.get("difficulty", TIER_DIFFICULTY.get(tier, 1000))),
        minutes=int(meta.get("minutes", TIER_MINUTES.get(tier, 15))),
        path=toml_path.parent,
        assessment=meta.get("assessment"),
        requires=list(meta.get("requires", [])),
    )


@lru_cache(maxsize=1)
def all_problems() -> dict[str, Problem]:
    found: dict[str, Problem] = {}
    base = paths.content_dir()
    if not base.exists():
        return found
    for toml_path in sorted(base.glob("*/*/problems/*/problem.toml")):
        p = load_problem(toml_path)
        found[p.id] = p
    return found


def problems_for_module(module_id: str) -> list[Problem]:
    probs = [p for p in all_problems().values() if p.module_id == module_id]
    return sorted(probs, key=lambda p: p.id)


def get(problem_id: str) -> Problem:
    probs = all_problems()
    if problem_id in probs:
        return probs[problem_id]
    matches = [p for pid, p in probs.items() if pid.endswith(problem_id) or problem_id in p.path.name]
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise KeyError(f"'{problem_id}' matches several problems: " + ", ".join(m.id for m in matches))
    raise KeyError(f"No problem '{problem_id}'. Problem ids look like core.02.p001")


def reload() -> None:
    all_problems.cache_clear()
