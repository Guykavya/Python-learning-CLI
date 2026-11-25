## Hint 1

Start with the single columns, then the pairs: both can be one loop over `k in (1, 2)` and `combinations(cols, k)`. How do you get the positions of each group?

## Hint 2

```text
overall = log_loss(y, p)
for k in (1, 2): for combo in combinations(cols, k):
    for key, idx in frame.groupby(list(combo)).indices.items():
        skip small or one-class groups
        name = " & ".join(f"{c}={v}" for c, v in zip(combo, atleast_1d(key)))
        found.append((name, len(idx), log_loss(y[idx], p[idx], labels=[0, 1]) - overall))
sort by gap descending, head(top), reset_index(drop=True)
```
