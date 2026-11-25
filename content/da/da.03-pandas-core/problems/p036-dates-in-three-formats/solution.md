## Approach

Start with a column of `NaT`. For each format in order, parse the whole stripped text with `errors="coerce"`, so only the rows that fit become dates, and `fillna` copies them into the rows that are still empty. Because `fillna` never overwrites a date that is already there, **the first matching format wins**; that is how `01/02/2024` follows your format order. After the loop, the rows that are still `NaT` although the input was not missing are the unparsed ones: report their **original** text.

## Code

```python
import pandas as pd


def parse_dates(s, formats):
    text = s.astype("string").str.strip()
    parsed = pd.Series(pd.NaT, index=s.index, dtype="datetime64[us]")
    for f in formats:
        parsed = parsed.fillna(pd.to_datetime(text, format=f, errors="coerce"))
    unparsed = s[parsed.isna() & s.notna()].tolist()
    return parsed, unparsed
```

## Complexity

O(k * n) for k formats: each format is one vectorised pass over the column. The loop is over formats (a handful), not over rows.

## Another way

Parse once per format and pick with `combine_first`: `first.combine_first(second)`. Or keep the first matching format per row with `np.select`. For a file whose date style follows a pattern, split the column by style first (`str.contains(r"^\d{4}-")`) and parse each group with one format: faster for millions of rows, and the style split becomes visible.
