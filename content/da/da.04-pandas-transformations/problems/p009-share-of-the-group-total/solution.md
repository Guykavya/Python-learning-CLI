## Approach

`transform("sum")` computes each store's total and broadcasts it back onto that store's rows, keeping the input's
index. Division then lines up label by label, whatever the index is. `assign` returns a new frame, so the caller's
frame is not changed. The quick self-check: the shares in each store add up to 1.

## Code

```python
import pandas as pd


def share_of_store(lines):
    total = lines.groupby("store_id")["revenue"].transform("sum")
    return lines.assign(share=lines["revenue"] / total)
```

## Complexity

O(n): one pass to sum per store and one to broadcast and divide.

## Another way

Aggregate and merge back: `totals = lines.groupby("store_id", as_index=False)["revenue"].sum()`, then a left merge on
`store_id` and a division. It is longer and the merge renumbers the index, so you have to restore it.
`transform` is the tool made for this.
