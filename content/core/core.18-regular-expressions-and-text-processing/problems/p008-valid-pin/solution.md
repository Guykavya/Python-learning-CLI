## Approach

- `[0-9]` is one ASCII digit.
- `{4,6}` repeats it four, five or six times.
- `re.fullmatch` requires the whole string to fit, so extra characters at either end fail.

## Code

```python
import re


def valid_pin(s: str) -> bool:
    return re.fullmatch(r"[0-9]{4,6}", s) is not None
```

## Complexity

O(n) for a string of length n (and at most 6 characters are ever accepted).

## Another way

`re.fullmatch(r"\d{4,6}", s, re.ASCII)`: the `ASCII` flag makes `\d` mean only `0`–`9`.

Without regex: `4 <= len(s) <= 6 and all(ch in "0123456789" for ch in s)`. Note that
`s.isdigit()` is not the same check: it is `True` for Devanagari digits and for `"²"`.
