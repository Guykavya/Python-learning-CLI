import re

ACRONYM_END_RE = re.compile(r"([A-Z]+)([A-Z][a-z])")
LOWER_UPPER_RE = re.compile(r"([a-z0-9])([A-Z])")
UNDERSCORE_RE = re.compile(r"(?<=[a-z0-9])_([a-z0-9])")


def to_snake(name: str) -> str:
    s = ACRONYM_END_RE.sub(r"\1_\2", name)
    s = LOWER_UPPER_RE.sub(r"\1_\2", s)
    return s.lower()


def to_camel(name: str) -> str:
    return UNDERSCORE_RE.sub(lambda m: m.group(1).upper(), name)
