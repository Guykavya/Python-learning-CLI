## Approach

`re.finditer(pattern, text)` returns an iterator of `Match` objects, one per non-overlapping match,
left to right. Each one knows its position: `m.span()` is `(m.start(), m.end())`. The end is
exclusive, exactly like a slice, so `text[m.start():m.end()] == m.group()`.

Zero-width matches (from `\b`, `^`, `a*`, lookarounds, the empty pattern) are real matches with
`start == end`. Since Python 3.7, an empty match may also sit right after a non-empty one, which is
why `a*` on `"baa"` gives `(1, 3)` and then `(3, 3)`.

## Code

```python
import re


def find_all_spans(pattern: str, text: str) -> list[tuple[int, int]]:
    return [m.span() for m in re.finditer(pattern, text)]
```

## Complexity

O(n) matching for simple patterns on text of length n (more for patterns that backtrack), and
O(k) memory for k matches.

## Another way

```python
spans = []
for m in re.finditer(pattern, text):
    spans.append((m.start(), m.end()))
```

Same result, spelled out. A compiled pattern works too: `re.compile(pattern).finditer(text)`.
