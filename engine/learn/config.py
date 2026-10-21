"""Read and edit config.toml while keeping its comments."""

from __future__ import annotations

import re
import tomllib
from typing import Any

from learn import paths

DEFAULTS: dict[str, dict[str, Any]] = {
    "accounts": {"codeforces_handle": "", "leetcode_username": ""},
    "plan": {"daily_minutes": 60, "focus": ["core", "dsa"]},
    "editor": {"open_in_vscode": False},
}


def load() -> dict[str, dict[str, Any]]:
    cfg = {section: dict(values) for section, values in DEFAULTS.items()}
    path = paths.config_path()
    if path.exists():
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        for section, values in data.items():
            if isinstance(values, dict):
                cfg.setdefault(section, {}).update(values)
    return cfg


def get(key: str) -> Any:
    section, _, name = key.partition(".")
    return load().get(section, {}).get(name)


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_format_value(v) for v in value) + "]"
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_cli_value(raw: str) -> Any:
    low = raw.lower()
    if low in ("true", "false"):
        return low == "true"
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if "," in raw:
        return [part.strip() for part in raw.split(",") if part.strip()]
    return raw


def set_value(key: str, value: Any) -> None:
    section, _, name = key.partition(".")
    if not section or not name:
        raise ValueError("Use section.name, for example plan.daily_minutes")
    path = paths.config_path()
    lines = path.read_text().splitlines() if path.exists() else []
    new_line = f"{name} = {_format_value(value)}"

    current = None
    section_end = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        m = re.fullmatch(r"\[([^\]]+)\]", stripped)
        if m:
            if current == section and section_end is None:
                section_end = i
            current = m.group(1).strip()
            continue
        if current == section and re.match(rf"{re.escape(name)}\s*=", stripped):
            lines[i] = new_line
            path.write_text("\n".join(lines) + "\n")
            return
    if current == section and section_end is None:
        section_end = len(lines)

    if section_end is not None:
        insert_at = section_end
        while insert_at > 0 and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines.insert(insert_at, new_line)
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines += [f"[{section}]", new_line]
    path.write_text("\n".join(lines) + "\n")
