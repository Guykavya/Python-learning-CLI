# Same groups, three shapes

Chapter section 4 (introduction table, 4.1 and 4.2). The same groups give three different shapes:

| Method | Returns | Shape |
|---|---|---|
| `agg` | one value per group | one row per group |
| `transform` | one value per original row | same index as the input |
| `filter` | the original rows of groups that pass | fewer rows, same columns |

```python
import pandas as pd

df = pd.DataFrame({
    "store": ["S1", "S2", "S1", "S3", "S2", "S1", "S3", "S1"],
    "rev": [10, 40, 20, 5, 50, 30, 15, 40],
})
g = df.groupby("store")["rev"]

a = g.agg("sum")
print(len(a), a.tolist())

t = g.transform("sum")
print(len(t), t.tolist())

f = df.groupby("store").filter(lambda d: d["rev"].sum() >= 90)
print(len(f), f.index.tolist())

m = df[g.transform("mean") > 15]
print(len(m), sorted(set(m["store"])))

print(df.groupby("store").size().tolist(), len(df.groupby("store").head(1)))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `e = pd.DataFrame({"k": ["x", "y", "x"], "v": [1, 2, 3]})`, `e.groupby("k")["v"].agg("sum").tolist()` is `[4, 2]`
(2 values), and `e.groupby("k")["v"].transform("sum").tolist()` is `[4, 2, 4]` (3 values, one per row).

## After you answer

- Lines 3 and 4 keep the same rows by two different routes. Which route calls a Python function once per group?
- Which of the five results could be assigned straight back as a new column of `df`?
