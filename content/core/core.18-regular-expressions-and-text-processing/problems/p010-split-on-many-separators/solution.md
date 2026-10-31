## Approach

- `[,;\s]` is one separator character. Inside a class, `\s` still means "any whitespace".
- `+` turns it into "a run of separators", so `a,,b` splits once.
- `re.split` still returns an empty string before a leading separator and after a trailing
  one, so filter the empties out.

## Code

```python
import re


def tokens(s: str) -> list[str]:
    return [part for part in re.split(r"[,;\s]+", s) if part]
```

## Complexity

O(n) for a string of length n.

## Another way

Instead of splitting on what you do **not** want, find what you **do** want:
`re.findall(r"[^,;\s]+", s)`. The negated class `[^,;\s]` is "any character that is not a
separator". `findall` never returns empty strings here (the `+` needs at least one character),
so no filter is needed.

Without regex: replace `,` and `;` with spaces and call `str.split()` with no argument, which
already splits on whitespace runs and drops empties: `s.replace(",", " ").replace(";", " ").split()`.
