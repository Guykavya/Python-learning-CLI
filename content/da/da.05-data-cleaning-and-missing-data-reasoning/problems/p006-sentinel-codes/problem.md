# Sentinel codes

Chapter section 3.3. A **sentinel** is a number that means "no answer" or "error": `-1`, `999`, `0` for an income. It
looks like data, so `mean` and `sum` use it. A few of them can move a mean by 18 years. The cure: replace a code that
*means missing* by a real missing value, and **count** what you replaced.

Write `replace_sentinels(df, codes)`:

- `codes` is a dict from a column name to the list of code values of that column, for example
  `{"age": [-1, 999], "income": [0]}`. The columns named in `codes` exist in `df`.
- Return a tuple `(new_df, counts)`.
- `new_df` is a **copy** of `df` in which every value listed for a column is replaced by a missing value. Columns not
  named in `codes` are untouched. The original `df` must not change.
- `counts` is a dict `{column: number of values replaced}` with **one key for every column in `codes`**, in the order of
  `codes`, including `0` for a column in which no code appeared. Values that were already missing are not counted.

## Example

```python
import pandas as pd

df = pd.DataFrame({
    "age": [25, -1, 999, 40, 999],
    "income": [0, 52000, 38000, 0, 41000],
    "city": ["Pune", "Delhi", "Pune", "Delhi", "Pune"],
})
out, counts = replace_sentinels(df, {"age": [-1, 999], "income": [0]})
print(out["age"].tolist())
print(out["income"].tolist())
print(counts)
print(df["age"].tolist())
print(round(df["age"].mean(), 1), round(out["age"].mean(), 1))
```

```text
[25.0, nan, nan, 40.0, nan]
[nan, 52000.0, 38000.0, nan, 41000.0]
{'age': 3, 'income': 2}
[25, -1, 999, 40, 999]
412.4 32.5
```

The integer columns became floats because a missing value needs `NaN`. Look at the last line: the mean age was 412.4
with the codes and 32.5 without them.
