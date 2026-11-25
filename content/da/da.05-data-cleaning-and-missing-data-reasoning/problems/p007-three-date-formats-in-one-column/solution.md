## Approach

Do not let one parser guess. The three formats are **recognisable by their shape**, so first match the shape with a
full-match pattern, then parse with the one format that belongs to it. Two kinds of failure are separated on purpose:
text that fits no shape (a fourth format has appeared) and text that fits a shape but is not a real date (an impossible
`31/04/2024`). Both become `NaT` and are listed in `bad`, so the caller sees *which* texts failed and can decide
(extend the patterns, or ask the data owner). Loud failure beats a silent wrong answer.

## Code

```python
import re
from datetime import datetime
import pandas as pd

FORMATS = [
    (r"[0-9]{4}-[0-9]{2}-[0-9]{2}", "%Y-%m-%d"),
    (r"[0-9]{2}/[0-9]{2}/[0-9]{4}", "%d/%m/%Y"),
    (r"[A-Z][a-z]{2} [0-9]{2}, [0-9]{4}", "%b %d, %Y"),
]


def parse_signup(s):
    values = []
    bad = set()
    for raw in s:
        if pd.isna(raw):
            values.append(pd.NaT)
            continue
        text = str(raw).strip()
        result = pd.NaT
        for pattern, fmt in FORMATS:
            if re.fullmatch(pattern, text):
                try:
                    result = pd.Timestamp(datetime.strptime(text, fmt))
                except ValueError:
                    pass
                break
        if result is pd.NaT:
            bad.add(text)
        values.append(result)
    return pd.Series(pd.to_datetime(values), index=s.index), sorted(bad)
```

## Complexity

O(n) values, each tried against at most three constant-size patterns.

## Another way

The chapter's column-wise version: for each `(pattern, format)` pair, `m = s.str.match(pattern)` and
`out[m] = pd.to_datetime(s[m], format=fmt)`, plus an `assert` that every row was claimed by exactly one pattern.
It is faster on a big column; with `errors="coerce"` it also handles impossible dates. The loop above is easier to read
and makes the `bad` list a by-product.
