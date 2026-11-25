## Hint 1

How can each frame "remember" its month before stacking? `assign` adds a column to a *copy*. After `pd.concat`, which
argument renumbers the rows, and how do you move one column to the front?

## Hint 2

```text
pieces = [frame.assign(month=key) for key, frame in frames.items()]
out = pd.concat(pieces, ignore_index=True)
order = ["month"] + every other column of out, in its current order
return out[order]
```
