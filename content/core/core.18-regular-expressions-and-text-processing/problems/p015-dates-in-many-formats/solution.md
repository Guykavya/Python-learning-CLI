## Approach

1. **One pattern, two alternatives**, so a single left-to-right scan finds both forms in text order:
   `([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})` or `([0-9]{4})-([0-9]{2})-([0-9]{2})`.
2. **Boundaries** `\b ... \b` around the whole alternation. They stop a match from starting
   inside a longer number (`112/05/2024`) or ending inside one (`12/05/20245`).
3. **`finditer`** gives Match objects. Groups 1-3 are filled for the slash form; groups 4-6 for
   the ISO form; the other three are `None`.
4. **Check and format**: convert to `int`, check the ranges, then format with `:02d` padding.

Regex checks the **shape** (digits and separators); Python checks the **values** (ranges).
Writing `(0?[1-9]|1[0-2])` for a month is possible, but it makes the pattern much harder to
read, and you still could not check days per month.

## Code

```python
import re

DATE_RE = re.compile(
    r"\b(?:([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})|([0-9]{4})-([0-9]{2})-([0-9]{2}))\b"
)


def find_dates(text: str) -> list[str]:
    result = []
    for m in DATE_RE.finditer(text):
        if m.group(1) is not None:
            day, month, year = m.group(1), m.group(2), m.group(3)
        else:
            year, month, day = m.group(4), m.group(5), m.group(6)
        d, mo = int(day), int(month)
        if 1 <= mo <= 12 and 1 <= d <= 31:
            result.append(f"{year}-{mo:02d}-{d:02d}")
    return result
```

## Complexity

O(n) for a text of length n.

## Another way

**Named groups** make the branches self-explaining: `(?P<d>...)/(?P<m>...)/(?P<y>...)`.
Python does not allow the same group name twice in one pattern, so the ISO branch needs other
names (`iy`, `im`, `id`), and `m.groupdict()` then tells you which ones are filled.

You could also run two separate `finditer` scans and sort the results by `m.start()`. That works,
but one combined pattern is simpler.

To check days per month as well, try `datetime.date(int(year), mo, d)` inside `try` /
`except ValueError` (it rejects 31 February).
