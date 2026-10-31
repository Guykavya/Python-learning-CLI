import re

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", re.MULTILINE)


def parse_hunks(text: str) -> list[tuple[int, int, int, int]]:
    hunks = []
    for m in HUNK.finditer(text):
        old_start, old_len, new_start, new_len = m.groups()
        hunks.append((
            int(old_start),
            int(old_len) if old_len is not None else 1,
            int(new_start),
            int(new_len) if new_len is not None else 1,
        ))
    return hunks
