"""Where everything lives. Set LEARN_HOME to point the engine at another folder."""

from __future__ import annotations

import os
import re
from pathlib import Path


def root() -> Path:
    env = os.environ.get("LEARN_HOME")
    if env:
        return Path(env).resolve()
    # engine/learn/paths.py -> project root is two levels above "engine"
    return Path(__file__).resolve().parents[2]


def content_dir() -> Path:
    return root() / "content"


def work_dir() -> Path:
    return root() / "my-work"


def playground_dir() -> Path:
    return root() / "playground"


def library_dir() -> Path:
    return root() / "library"


def data_dir() -> Path:
    return root() / "data"


def db_path() -> Path:
    return data_dir() / "progress.db"


def config_path() -> Path:
    return root() / "config.toml"


def syllabus_path() -> Path:
    return root() / "syllabus.yaml"


def slugify(text: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-")
