## Hint 1

What do you compute for one stratum, and what must be true of that stratum before you can? How do you decide the weight of each stratum, and which strata are in the weights?

## Hint 2

```text
for name, g in df.groupby(by):
    t, c = g[g[treat] == 1][outcome], g[g[treat] == 0][outcome]
    if t.empty or c.empty: skipped.append(name); continue
    diffs.append(t.mean() - c.mean()); sizes.append(len(g))
adjusted = np.average(diffs, weights=sizes)
```
