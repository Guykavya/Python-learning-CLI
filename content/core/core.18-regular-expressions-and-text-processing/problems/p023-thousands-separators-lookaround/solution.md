## Approach

Do not look for digits to replace; look for **gaps** to fill. A gap needs a comma when:

1. there is a digit on its left: `(?<=\d)`, and
2. the digits on its right, all the way to the end, come in whole groups: `(?=(?:\d{3})+$)`.

Both parts are lookarounds, so the whole pattern is zero-width. `re.sub(pattern, ",", s)` finds
each such empty match and replaces "nothing" with a comma, which inserts it.

Why each piece matters:

- Without `$`, the lookahead only asks "are there at least three digits ahead?", which is true
  at almost every gap: `1,2,3,4,567`.
- Without `(?<=\d)`, the gap before the first digit of `123` qualifies (three digits to the
  right), giving `,123`; for `-123` you would get `-,123`.

For Indian grouping only the "group shape" changes: the digits on the right must be any number
of pairs followed by the final three, `(?=(?:\d\d)*\d{3}$)`.

## Code

```python
import re

WESTERN_RE = re.compile(r"(?<=\d)(?=(?:\d{3})+$)")
INDIAN_RE = re.compile(r"(?<=\d)(?=(?:\d\d)*\d{3}$)")


def commas(n: int) -> str:
    return WESTERN_RE.sub(",", str(n))


def commas_indian(n: int) -> str:
    return INDIAN_RE.sub(",", str(n))
```

## Complexity

At each of the d gaps the lookahead scans to the end of the string: O(d²) for d digits. For
numbers people read, d is tiny.

## Another way

For Western grouping Python has it built in: `f"{n:,}"` gives `'1,234,567'`. There is no format
code for Indian grouping, so you would write a loop: take the last three digits, then slice off
two at a time from the right and join with commas. The regex is shorter, and the same idea
(zero-width lookarounds + `re.sub`) inserts any separator anywhere.
