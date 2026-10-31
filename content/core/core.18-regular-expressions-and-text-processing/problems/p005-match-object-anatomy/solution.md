## Approach

`re.search` gives a Match object or `None`. Check for `None` first, then read the three pieces
of information out of the Match object.

## Code

```python
import re


def span_info(pattern: str, text: str) -> tuple[str, int, int] | None:
    m = re.search(pattern, text)
    if m is None:
        return None
    return (m.group(0), m.start(), m.end())
```

`m.group()` and `m.group(0)` are the same: group 0 is always the whole match.

## Complexity

O(n) for typical patterns on a text of length n (the cost depends on the pattern in general).

## Another way

`m.span()` returns `(start, end)` in one call, so `return (m.group(), *m.span())` builds the same tuple.
