## Approach

Follow the rules in order. Missing is checked **before** cleaning, so `"-"` is missing but `"-5"` is a negative number. Finite-checking stops `"inf"` and `"nan"`-like words from slipping through `float`.

## Code

```python
import math

MISSING = {"", "na", "n/a", "nan", "null", "none", "-", "?"}

def parse_number(text):
    t = text.strip().lower()
    if t in MISSING:
        return None
    for junk in ("rs.", "rs", "ms", "%", "$"):
        t = t.replace(junk, "")
    t = t.replace(",", "").replace(" ", "")
    try:
        x = float(t)
    except ValueError:
        raise ValueError(f"cannot parse {text!r}") from None
    if not math.isfinite(x):
        raise ValueError(f"cannot parse {text!r}")
    return x
```

## Complexity

O(length of the text).

## Another way

A regular expression for the whole grammar is shorter to run but harder to read; `re` has not been needed in this module. Libraries such as pandas apply the same ideas with `pd.to_numeric(errors="coerce")`, which hides the reason, so keep your own helper when you want to report what was dropped.

Note: removing every `"ms"` or `"rs"` is crude (it would also damage words), but a cell that still contains letters after cleaning fails in `float` and is reported.
