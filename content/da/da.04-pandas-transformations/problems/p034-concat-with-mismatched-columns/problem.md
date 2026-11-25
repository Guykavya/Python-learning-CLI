# `concat` with mismatched columns

Chapter section 7.3. `concat` lines tables up **by name**: column names when it stacks (`axis=0`), index labels when it
puts tables side by side (`axis=1`). Whatever does not line up becomes missing, silently.

```python
import pandas as pd

a = pd.DataFrame({"id": [1, 2], "qty": [5, 6]})
b = pd.DataFrame({"id": [3], "price": [9.5]})

c = pd.concat([a, b], ignore_index=True)
print(c.shape, list(c.columns))
print(int(c.isna().sum().sum()), c["qty"].isna().tolist())

i = pd.concat([a, b], join="inner", ignore_index=True)
print(i.shape, list(i.columns))

x = pd.Series([1, 2], index=["p", "q"], name="x")
y = pd.Series([10, 20], index=["q", "r"], name="y")
s = pd.concat([x, y], axis=1)
print(s.shape, s.index.tolist())
print(s["x"].tolist())
print(s["y"].tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

`pd.concat([pd.DataFrame({"k": [1]}), pd.DataFrame({"k": [2], "v": [7]})], ignore_index=True)` has shape `(2, 2)`:
the first row has no `v`, so it gets `NaN` there, and the column `v` becomes `float64` (`[nan, 7.0]`).

## After you answer

- Why does the `qty` column of `c` print as floats if you call `c["qty"].tolist()`?
- When is `join="inner"` dangerous, and what would you check before stacking two files?
