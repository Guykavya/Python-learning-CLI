# Ranks inside groups

Chapter section 5.2 (and the `rank_in_store` exercise in 4.3). `groupby(...)[col].rank()` ranks each row **within its
group** and keeps the original index. The `method` decides what happens with ties:

| `method` | Two rows tie for 1st place |
|---|---|
| `"average"` (default) | both get 1.5, the next gets 3 |
| `"min"` | both get 1, the next gets 3 |
| `"dense"` | both get 1, the next gets 2 |
| `"first"` | 1 and 2, in order of appearance |

```python
import pandas as pd

df = pd.DataFrame({
    "store": ["S1", "S1", "S2", "S1", "S2", "S2", "S1"],
    "revenue": [50, 80, 30, 80, 90, 30, 20],
})
g = df.groupby("store")["revenue"]

print(g.rank(method="dense", ascending=False).tolist())
print(g.rank(method="min", ascending=False).tolist())
print(g.rank(method="first", ascending=False).astype(int).tolist())
print(g.rank(ascending=False).tolist())

r = g.rank(method="dense", ascending=False)
print(df.index[r == 1].tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `pd.Series([5, 7, 5]).rank(method="min", ascending=False).tolist()` the answer is `[2.0, 1.0, 2.0]`: 7 is first,
the two 5s share second place. `rank` returns floats (because of `"average"`), so the lists print `2.0`, not `2`.

## After you answer

- For a "top 2 per store" report that must return exactly 2 rows per store, which method do you need?
- Which method answers "is this one of the two best **revenue levels** of the store"?
