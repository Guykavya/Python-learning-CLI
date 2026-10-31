## Approach

The shape is fixed: an optional `v`, digits, dot, digits, dot, digits. Write it as a pattern
with one capturing group per number:

```
[vV]?(\d+)\.(\d+)\.(\d+)
```

- `[vV]?` is outside any group, so it is matched but not captured.
- `\.` is an escaped dot: a real full stop. A bare `.` would match any character.
- `re.fullmatch` demands that the pattern covers the *whole* string, so `1.2.3.4` and
  `1.2.3-beta` fail. With `re.match` they would succeed on the `1.2.3` prefix.

`m.groups()` returns all the captured texts as a tuple of strings, in the order their `(`
appear. Unpack it and convert each part with `int`.

## Code

```python
import re

VERSION_RE = re.compile(r"[vV]?(\d+)\.(\d+)\.(\d+)")


def parse_version(s: str) -> tuple[int, int, int] | None:
    m = VERSION_RE.fullmatch(s.strip())
    if m is None:
        return None
    major, minor, patch = m.groups()
    return (int(major), int(minor), int(patch))
```

## Complexity

O(n) for a string of length n: the pattern has no nested repetition, so each character is
looked at a small fixed number of times.

## Another way

Without regex: strip, remove one leading `v`/`V`, `split(".")`, check there are exactly three
parts and that each `part.isdigit()`. That works here, but every extra rule (an optional
`-beta` suffix, say) adds more `if`s, while the pattern grows by one piece.

You could also write `tuple(map(int, m.groups()))`.
