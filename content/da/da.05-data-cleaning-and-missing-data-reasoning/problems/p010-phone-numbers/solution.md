## Approach

Two small steps instead of one clever pattern (the chapter's advice: a pattern you cannot explain in one sentence
should be split). Step 1 removes decoration, so six styles become one string of digits. Step 2 removes a country code or
a trunk zero **only if exactly ten digits follow**, which is what the lookahead `(?=\d{10}$)` says. That condition is
the whole difference between `+91 98765 43210` (prefix removed) and `9123456789` (the `91` belongs to the number). Last,
`fullmatch` checks the shape: ten digits, first digit 6 to 9. Anything else is not a mobile number: missing, never a
crash, never a guess.

## Code

```python
import pandas as pd


def clean_phone(s):
    digits = s.str.replace(r"\D", "", regex=True)
    digits = digits.str.replace(r"^(?:91|0)(?=[0-9]{10}$)", "", regex=True)
    return digits.where(digits.str.fullmatch(r"[6-9][0-9]{9}", na=False))
```

## Complexity

O(n) over the rows; each pattern is applied once per value and is linear in the length of the text.

## Another way

Without a lookahead, use the length: after removing non-digits, if the text has 12 digits and starts with `91`, or 11
digits and starts with `0`, cut the prefix with `digits.str[-10:]`; ten digits stay as they are. It is longer but each
line is easy to read. A column-wise version is also good for a million rows; a loop over Python strings is fine for a
few thousand.
