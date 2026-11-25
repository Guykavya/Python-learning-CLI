# Old labels stay after a filter

Chapter sections 4.1 and 7.2. A filtered frame keeps the **old labels** of the rows it kept. Positions start again at 0.

```python
import pandas as pd

df = pd.DataFrame({"n": [5, 6, 7, 8], "name": ["a", "b", "c", "d"]})
kept = df[df["n"] > 5]

print(kept.index.tolist())
print(kept.shape)
try:
    print(kept.loc[0, "n"])
except KeyError as exc:
    print(type(exc).__name__)
print(int(kept["n"].iloc[0]))
print(int(kept.loc[2, "n"]))

fresh = kept.reset_index(drop=True)
print(fresh.index.tolist())
print(int(fresh.loc[0, "n"]))
print(kept.reset_index().columns.tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `t = pd.DataFrame({"v": [1, 2, 3]})` and `u = t[t["v"] != 1]`, `u.index.tolist()` prints `[1, 2]`, `u["v"].iloc[0]`
is `2`, and `u.loc[0, "v"]` raises `KeyError`.

## After you answer

- Which two lines of the program use *labels*, and which one uses a *position*?
- What does `reset_index()` without `drop=True` add, and when do you want it?
