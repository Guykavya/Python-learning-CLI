# Count the rows through a pipeline

Chapter sections 11.2, 14.4 and 17.1, and the audit habit of 19.4. A cleaning pipeline loses rows at every step, and a
good analyst knows **how many and why**. Here is a ten-row table pushed through four steps. After each step the
program prints how many rows are left.

```python
import pandas as pd

df = pd.DataFrame({
    "id":   [1, 2, 2, 3, 4, 5, 5, 6, 7, 8],
    "city": ["Pune", "Delhi", "Delhi", None, "Agra", "Pune", "Pune", "Delhi", "Agra", "Pune"],
    "qty":  [3, 5, 5, 2, None, 4, 6, 1, 8, 4],
})
print(len(df))

a = df.dropna(subset=["city"])
print(len(a))
b = a.drop_duplicates()
print(len(b), int(b["qty"].isna().sum()))
c = b[b["qty"] > 2]
print(len(c))
d = c.drop_duplicates(subset=["id"], keep="last")
print(len(d))

print(d["id"].tolist())
print(d["qty"].tolist())
print(d.index.tolist())
print(str(d["qty"].dtype), len(df))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Remember three rules from the
chapter: `drop_duplicates()` with no arguments compares **whole rows**; a comparison with a missing value (`NaN > 2`) is
`False`; and `keep="last"` keeps the last row of each group of equal keys. A column of integers with one missing value
is stored as floats.

Do not run the code before you have written your answer.

## Example

For `pd.DataFrame({"k": [1, 1, 2]})`, `len(df.drop_duplicates())` is `2` and
`df.drop_duplicates(subset=["k"], keep="last").index.tolist()` is `[1, 2]`.

## After you answer

- Row 4 (`id` 4) has a missing `qty`. Which step removed it, and was that the step you would have *chosen* for it?
- Two rows have `id` 5 but different `qty`. Which one survived, and what would `keep="first"` have kept instead?
