# `profile`: one screen per table

Chapter section 18.1 (the first thing you do with a new table). Write `profile(df, top=3)` that returns a DataFrame with
**one row per column of `df`** (the index holds the column names, in the original order) and these columns:

| column | meaning |
|---|---|
| `dtype` | the dtype as text (`str(s.dtype)`) |
| `missing` | how many values are missing (an `int`) |
| `unique` | how many **distinct non-missing** values (an `int`) |
| `top` | a list of `(value, count)` pairs for the `top` most frequent non-missing values, most frequent first; equal counts ordered by value (smallest first); counts are plain `int`s |
| `min`, `max` | the smallest and largest value for **numeric** columns (integers and floats, **not** booleans), as floats; `NaN` for every other kind of column and for a numeric column with no values |

Use pandas methods per column (`isna`, `nunique`, `value_counts`, `min`, `max`); the only loop allowed is over the
**columns**. The input frame is not changed. (The chapter's `profile` also prints and shows an example value; here you
return a table, which is easier to test and to reuse.)

## Example

```python
import pandas as pd

from solution import profile

df = pd.DataFrame({
    "city": ["Pune", "Agra", "Pune", None, "Agra", "Delhi"],
    "qty": [1, 2, 2, 2, None, 5],
    "paid": [True, False, True, True, True, False],
})
p = profile(df, top=2)
print(p.index.tolist(), p.columns.tolist())
print(p.loc["city", "top"], p.loc["city", "missing"], p.loc["city", "unique"])
print(p.loc["qty", "top"], p.loc["qty", "min"], p.loc["qty", "max"], p.loc["qty", "dtype"])
print(p.loc["paid", "top"], p.loc["paid", "min"])
```

```text
['city', 'qty', 'paid'] ['dtype', 'missing', 'unique', 'top', 'min', 'max']
[('Agra', 2), ('Pune', 2)] 1 3
[(2.0, 3), (1.0, 1)] 1.0 5.0 float64
[(True, 4), (False, 2)] nan
```
