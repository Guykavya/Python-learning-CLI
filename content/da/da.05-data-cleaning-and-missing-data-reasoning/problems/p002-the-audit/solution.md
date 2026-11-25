## Approach

Treat the audit as five small questions asked of every column, collected into one row. Three of them are direct
pandas calls (`dtype`, `isna().sum()`, `nunique()`), `top` comes from `value_counts()`, and the new one,
`suspect_text`, answers the chapter's central trap: missing values hiding behind fake text. A text column in which
most values parse as numbers is a number column that someone typed into carelessly; the values that do not parse are
exactly what a later cleaning step must look at. A column of names or cities is mostly *not* numbers, so it is left
alone (`0`), which keeps the audit from crying wolf.

## Code

```python
import pandas as pd


def audit(df):
    rows = []
    for name in df.columns:
        s = df[name]
        present = s.dropna()
        top = None
        if len(present) > 0:
            counts = present.value_counts()
            best = counts.max()
            top = sorted(counts[counts == best].index)[0]
        suspect = 0
        if pd.api.types.is_string_dtype(s) and len(present) > 0:
            parsed = pd.to_numeric(present.str.strip(), errors="coerce")
            ok = parsed.notna()
            if ok.sum() * 2 > len(present):
                suspect = int((~ok).sum())
        rows.append({
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "unique": int(present.nunique()),
            "top": top,
            "suspect_text": suspect,
        })
    return pd.DataFrame(rows, index=list(df.columns),
                        columns=["dtype", "missing", "unique", "top", "suspect_text"])
```

## Complexity

O(rows x columns): each column is scanned a constant number of times. `value_counts` hashes every value.

## Another way

A column-wise version without the loop: `pd.DataFrame({"dtype": df.dtypes.astype(str), "missing": df.isna().sum(),
"unique": df.nunique()})` gives three of the five columns in one expression (this is the chapter's `audit`). The loop is
only needed for `top` (ties) and `suspect_text` (a rule per column). Another approach for `suspect_text` is a regular
expression such as `fullmatch(r"\s*-?\d+(\.\d+)?\s*")`; `to_numeric` is shorter and also accepts `1e3`.
