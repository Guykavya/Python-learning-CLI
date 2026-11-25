# What does iterating a groupby give?

Chapter section 2.5. A `GroupBy` object is iterable: each step gives a **key** and the **sub-table** of that group,
with the original row labels. The order is sorted by key, unless `sort=False` keeps the order of first appearance.

```python
import pandas as pd

df = pd.DataFrame({"k": ["b", "a", "c", "a", "b", "a"], "v": [1, 2, 3, 4, 5, 6]})
for key, part in df.groupby("k"):
    print(key, len(part), part["v"].tolist())

g = df.groupby("k", sort=False)
print([key for key, _ in g])
print(g.ngroups, df.groupby("k").get_group("b").index.tolist())

for key, part in df.groupby(["k"]):
    print(repr(key), part.index.tolist())
    break
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `e = pd.DataFrame({"k": ["y", "x", "y"]})`, `[key for key, _ in e.groupby("k")]` is `['x', 'y']`, and
`e.groupby("k").get_group("y").index.tolist()` is `[0, 2]`: the sub-table keeps the original labels.

## After you answer

- Why is the key on the last line a tuple although there is only one key column?
- When would you write `sort=False`?
