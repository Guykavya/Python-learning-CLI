## Approach

The grain of `targets` is (store, day), so the key is the pair: `on=["store_id", "date"]`. A left join keeps every
sales row; `validate="m:1"` confirms that each (store, day) has at most one target, so no row can be duplicated.
Comparing with a missing target gives `False`, which is exactly the rule "no target, no hit".

## Code

```python
import pandas as pd


def daily_targets(sales, targets):
    out = sales.merge(targets[["store_id", "date", "target"]], on=["store_id", "date"], how="left", validate="m:1")
    out["hit"] = out["revenue"] >= out["target"]
    return out
```

## Complexity

O(n + t): a hash join on the pair of keys.

## Another way

Index both tables by the pair and `join`: `sales.join(targets.set_index(["store_id", "date"])["target"],
on=["store_id", "date"])`. Same rows; `merge` with `on=[...]` is usually clearer.
