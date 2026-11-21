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
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "on"):
        return True
    if text in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"not a yes/no value: {value!r}")


def _level(value):
    level = str(value).upper()
    if level not in LEVELS:
        raise ValueError(f"log level must be one of {', '.join(LEVELS)}")
    return level


def load(path=None, env=None, flags=None):
    """(Settings, sorted unknown keys of the file). defaults < file < env TIDY_* < flags."""
    env = os.environ if env is None else env
    raw, sources, unknown = dict(DEFAULTS), {k: "default" for k in DEFAULTS}, []
    if path and Path(path).exists():
        for key, value in tomllib.loads(Path(path).read_text(encoding="utf-8")).items():
            if key in DEFAULTS:
                raw[key], sources[key] = value, "file"
            else:
                unknown.append(key)
    for key in DEFAULTS:
        value = env.get(ENV_PREFIX + key.upper(), "")
        if value != "":
            raw[key], sources[key] = value, "env"
    for key, value in (flags or {}).items():
        if key in DEFAULTS and value is not None:
            raw[key], sources[key] = value, "flag"

    def convert(name, fn):
        try:
            return fn(raw[name])
        except (ValueError, TypeError) as e:
            raise ValueError(f"{name} from {sources[name]}: {raw[name]!r} ({e})") from e

    settings = Settings(folder=convert("folder", lambda v: Path(str(v)).expanduser()),
                        keep_days=convert("keep_days", int),
                        dry_run=convert("dry_run", to_bool),
                        log_level=convert("log_level", _level),
                        api_token=env.get(ENV_PREFIX + "API_TOKEN") or None,
                        sources=sources)
    return settings, sorted(unknown)
