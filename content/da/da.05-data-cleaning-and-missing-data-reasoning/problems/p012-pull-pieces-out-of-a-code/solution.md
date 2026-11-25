## Approach

Write the shape of the code once, as a pattern with **named groups**, and let `str.extract` do the cutting: the group
names become the column names, and a row that does not match becomes a row of `NaN` (the chapter calls this out:
no match gives a missing value, never an error). Anchors `^` and `$` make the match cover the whole text, so
`EL-2024-0042-extra` cannot slip through. Then convert the digit columns. `Int64` (capital I) holds integers *and* a
missing value; plain `int` cannot.

## Code

```python
import pandas as pd

CODE = r"^(?P<category>[A-Z]{2})-(?P<year>[0-9]{4})-(?P<number>[0-9]{4})$"


def split_product_code(s):
    parts = s.str.strip().str.extract(CODE)
    parts["year"] = pd.to_numeric(parts["year"]).astype("Int64")
    parts["number"] = pd.to_numeric(parts["number"]).astype("Int64")
    return parts
```

## Complexity

O(n) for the pattern, O(n) for the conversions.

## Another way

`s.str.split("-", expand=True)` is shorter, but it cuts anything with a hyphen and fills extra columns without
complaining, so it cannot tell a good code from a bad one. `extract` with a pattern is both the cutter and the checker:
`parts.isna().any(axis=1).sum()` counts the codes that did not follow the shape.
