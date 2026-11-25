# Inclusive or exclusive slice?

Chapter section 7. A slice by **label** (`loc`) includes both ends. A slice by **position** (`iloc`) stops *before* the
end, like a Python list.

```python
import pandas as pd

df = pd.DataFrame(
    {"x": [1, 2, 3, 4], "y": [5, 6, 7, 8], "z": [9, 10, 11, 12]},
    index=["a", "b", "c", "d"],
)

r = df.loc["b":"d"]
print(r.shape, r.index.tolist())
r = df.iloc[1:3]
print(r.shape, r.index.tolist())
r = df.loc[:, "x":"z"]
print(r.shape, r.columns.tolist())
r = df.iloc[:, 1:]
print(r.shape, r.columns.tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `t = pd.DataFrame({"p": [1, 2, 3]}, index=["u", "v", "w"])`, `t.loc["u":"v"]` has shape `(2, 1)` and index `['u', 'v']`
(both ends in), while `t.iloc[0:1]` has shape `(1, 1)` and index `['u']`.

## After you answer

- Which two of the four slices include their end point?
- You want "rows b to d" as positions. Which `iloc` slice gives exactly the first slice's rows?
