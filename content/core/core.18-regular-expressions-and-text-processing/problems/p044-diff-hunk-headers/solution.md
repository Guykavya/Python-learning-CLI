## Approach

- `^` with `re.MULTILINE` anchors the pattern to the start of **each** line, so `-@@ ...` (a
  removed line) and ` @@ ...` (a context line) are ignored.
- `-(\d+)` and `\+(\d+)` capture the starts. `+` must be escaped: unescaped it is a quantifier.
- `(?:,(\d+))?` is an optional non-capturing block holding a capturing group. If the `,B` part
  is missing, the group did not take part and `m.group(2)` is `None`. That is how "missing" is
  told apart from `0`.
- `finditer` walks all headers; each match's four groups become ints, with `None` → 1.
- Nothing after the second `@@` is matched, so headings are allowed.

## Code

```python
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
```

## Complexity

O(n) over the diff text. Memory O(h) for h hunks.

## Another way

`m.groups(default="1")` fills groups that did not take part with `"1"` instead of `None`:

```python
a, b, c, d = m.groups(default="1")
hunks.append((int(a), int(b), int(c), int(d)))
```

Or loop over `text.splitlines()` and use `HUNK.match(line)` (no `MULTILINE` needed then, because
`match` only tries the start of each line).
