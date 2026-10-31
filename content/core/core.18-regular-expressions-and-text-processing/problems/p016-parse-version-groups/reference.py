import re

VERSION_RE = re.compile(r"[vV]?(\d+)\.(\d+)\.(\d+)")


def parse_version(s: str) -> tuple[int, int, int] | None:
    m = VERSION_RE.fullmatch(s.strip())
    if m is None:
        return None
    major, minor, patch = m.groups()
    return (int(major), int(minor), int(patch))
