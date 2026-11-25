## Approach

The chapter's order, with more rules: first decide what is a *code for missing*, then peel decoration off the two
ends, handle the `k`, remove commas, and only then check that what is left is a plain number. The last check is the
important one: it lets the function refuse text it cannot read (`NaN`) without ever crashing and without guessing, and
it rejects things `float()` would accept by surprise (`"1e5"`, `"inf"`, `"-5000"`). Rules that look like a list of
special cases are really a small grammar: `[mark] number [k] [/-]`.

## Code

```python
import re
import pandas as pd

NA_TEXT = {"", "n/a", "-999"}


def _parse_one(value):
    if value is None or pd.isna(value):
        return float("nan")
    text = str(value).strip().lower()
    if text in NA_TEXT:
        return float("nan")
    text = re.sub(r"^(₹|rs\.?)\s*", "", text)
    text = re.sub(r"/-$", "", text).strip()
    factor = 1
    if text.endswith("k"):
        factor = 1000
        text = text[:-1].strip()
    text = text.replace(",", "")
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", text):
        return float("nan")
    return float(text) * factor


def parse_income(s):
    return pd.Series([_parse_one(v) for v in s], index=s.index, dtype="float64")
```

## Complexity

O(n) values, each processed with a few small regex operations (constant work per value).

## Another way

Column-wise: `t = s.str.strip().str.lower()`, `t = t.mask(t.isin(NA_TEXT))`, then
`t.str.replace(r"^(₹|rs\.?)\s*", "", regex=True)` and so on, ending with `pd.to_numeric(t, errors="coerce")`. It is
shorter, and faster on a million rows, but the `k` rule needs `str.extract` to get the factor, and `coerce` hides what
failed. The loop is easier to debug: print the values that came out as `NaN` and read them.
