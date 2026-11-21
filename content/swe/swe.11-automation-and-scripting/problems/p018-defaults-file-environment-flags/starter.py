import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULTS = {"folder": "~/Downloads", "keep_days": 30, "dry_run": True, "log_level": "WARNING"}
ENV_PREFIX = "TIDY_"
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


@dataclass(frozen=True)
class Settings:
    folder: Path
    keep_days: int
    dry_run: bool
    log_level: str
    api_token: str | None = field(default=None, repr=False)              # repr=False: never printed by accident
    sources: dict = field(default_factory=dict, repr=False, compare=False)  # setting name -> "default"/"file"/"env"/"flag"


def to_bool(value):
    """True/False from a bool or from 1/true/yes/on and 0/false/no/off (any case); else ValueError."""
    # TODO
    raise NotImplementedError


def load(path=None, env=None, flags=None):
    """(Settings, sorted unknown keys of the file). defaults < file < env TIDY_* < flags."""
    # TODO
    raise NotImplementedError
