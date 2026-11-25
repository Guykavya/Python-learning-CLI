## Approach

A lookup table of factors, a normalised key, and a loud failure. The table is the documentation: it lists every unit the
pipeline understands. An unknown unit means the table is incomplete or the data is wrong; either way a person should
decide, so the function raises instead of guessing a factor. Missing values pass through as `nan`, so a later `mean`
skips them as usual.

## Code

```python
FACTORS = {"g": 0.001, "kg": 1.0, "lb": 0.45359237}


def to_kg(values, units):
    out = []
    for value, unit in zip(values, units):
        key = str(unit).strip().lower()
        if key not in FACTORS:
            raise ValueError("unknown unit %r" % str(unit).strip())
        if value is None or value != value:
            out.append(float("nan"))
        else:
            out.append(float(value) * FACTORS[key])
    return out
```

## Complexity

O(n), one dictionary lookup per value.

## Another way

In pandas: `df["weight_kg"] = df["value"] * df["unit"].str.strip().str.lower().map(FACTORS)`. A unit not in the table
becomes `NaN` silently, so add the check `unknown = df.loc[factor.isna() & df["unit"].notna(), "unit"].unique()` and
raise if it is not empty. The explicit loop has the failure built in.
