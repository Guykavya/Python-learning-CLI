# Chained assignment in pandas 3

Chapter sections 9.2 and 9.3. pandas 3 uses **Copy-on-Write**: a Series taken from a DataFrame, or any result of an
operation, behaves like its own copy. Changing it never changes the parent. A plain second name for the **same** object
(`y = x`) is not a copy.

```python
import warnings

import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    df[df["a"] > 1]["b"] = 0
print(df["b"].tolist())
print(len(caught), type(caught[0].message).__name__)

s = df["a"]
s.iloc[0] = 99
print(df["a"].tolist(), s.tolist())

df.loc[df["a"] > 1, "b"] = 0
print(df["b"].tolist())

x = pd.Series([1, 2, 3])
y = x
y.iloc[0] = 9
print(x.tolist())
z = x.copy()
z.iloc[1] = 50
print(x.tolist(), z.tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

If `w = pd.Series([1, 2])` and `v = w.copy()` and then `v.iloc[0] = 7`, then `w.tolist()` is `[1, 2]` and `v.tolist()` is
`[7, 2]`. With `v = w` instead, both lists would be `[7, 2]` (one object, two names).

## After you answer

- Why did the first assignment change nothing, and what is the one-line fix (the third block)?
- In what way is `y = x` different from `s = df["a"]`, although both are "another name"?
