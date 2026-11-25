# Four kinds of "missing"

Chapter sections 3.3 and 7.1. A table from a file often hides its missing values in text: an empty cell, a cell with
only spaces, `"NA"`, `"n/a"`, `"-"`. To pandas these are ordinary words, so `isna()` says `False` and a count of
"missing" is too small. Turn them into **real** missing values first.

Write `to_missing(df, tokens=("", "NA", "n/a", "-"))`:

- For every column that is **not numeric and not a datetime**, a value becomes a real missing value when, after
  removing spaces at both ends, it equals one of the `tokens`, ignoring upper and lower case. (So `"  "` and `"N/A"`
  and `" - "` all become missing; the token `""` therefore also catches whitespace-only text.)
- Numeric and datetime columns are not touched.
- Return `(clean, counts)`: `clean` is a **new** frame (same columns, same index, other values unchanged) and
  `counts` is a dict `{column: number of values that were turned into missing}` with an entry for **every** column
  (`0` for numeric columns). Values that were already missing are not counted.
- Do not change `df`.

## Example

```python
import pandas as pd

d = pd.DataFrame({"city": ["Pune", " ", "n/a", "NA", "Delhi", None],
                  "n": [1, 2, 3, 4, 5, 6],
                  "note": ["ok", "-", "", "fine", "  - ", "x"]})
clean, counts = to_missing(d)
print(clean)
print(counts)
```

```text
    city  n  note
0   Pune  1    ok
1    NaN  2   NaN
2    NaN  3   NaN
3    NaN  4  fine
4  Delhi  5   NaN
5    NaN  6     x
{'city': 3, 'n': 0, 'note': 3}
```

The `None` in `city` was already missing, so it is not counted: `city` has 3 conversions (`" "`, `"n/a"`, `"NA"`).
