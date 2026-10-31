## Approach

`re.search` tries the pattern at position 0, then 1, then 2, and so on, and stops at the first
place it fits. For the one-character pattern `\d` that means "the first digit in the string".
If it never fits, it returns `None`.

The function must return a `bool`, so compare the result with `None`.

## Code

```python
import re


def has_digit(s: str) -> bool:
    return re.search(r"\d", s) is not None
```

The `r` in front of `"\d"` makes it a **raw string**, so the backslash reaches the regex engine
unchanged. Always write patterns as raw strings.

## Complexity

O(n) for a string of length n: one left-to-right scan.

## Another way

Without regex: `any(ch.isdigit() for ch in s)`. For a single "is there a digit" question this
is just as good and maybe clearer. Regex starts to pay off once the pattern has more than one
part, such as "a digit followed by a letter".

Note: `\d` matches any Unicode digit, for example the Devanagari digit `४`. So does
`str.isdigit()`. If you only want `0`–`9`, write `[0-9]`.
