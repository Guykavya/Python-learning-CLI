## Approach

- `[0-9a-fA-F]` is one hex digit: three ranges in one class.
- `+` repeats it one or more times, so the empty string fails.
- `re.fullmatch` demands that the match covers all of `s`. Any other character anywhere makes it fail.

## Code

```python
import re


def only_hex(s: str) -> bool:
    return re.fullmatch(r"[0-9a-fA-F]+", s) is not None
```

## Complexity

O(n) for a string of length n.

## Another way

- `re.fullmatch(r"[0-9a-f]+", s, re.IGNORECASE)` uses a flag instead of listing both cases.
- Without regex: `s != "" and all(ch in "0123456789abcdefABCDEF" for ch in s)`.
- `int(s, 16)` is **not** a good check: it accepts `" ff "`, `"0xff"`, `"f_f"` and `"-ff"`.
