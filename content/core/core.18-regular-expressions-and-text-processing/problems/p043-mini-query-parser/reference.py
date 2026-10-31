import re

TERM = re.compile(
    r"""
    (?: (?P<key>\w+) : )?           # optional  key:
    (?:
        "(?P<quoted>[^"]*)"         # a quoted phrase ...
      | (?P<word>\S+)               # ... or a run of non-space characters
    )
    """,
    re.VERBOSE,
)


def parse_query(q: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for m in TERM.finditer(q):
        key = m.group("key")
        key = key.lower() if key is not None else "_"
        value = m.group("quoted") if m.group("quoted") is not None else m.group("word")
        result.setdefault(key, []).append(value)
    return result
