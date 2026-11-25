## Approach

Both tools align on labels, so first make `customer_id` the index of both tables. `DataFrame.update` overwrites cells
of the calling frame with the **non-missing** cells of the other frame, only for labels and columns the caller already
has. That is exactly the rule. `update` works in place, so call it on the new frame made by `set_index`, never on
`old`. Then turn the id back into a column.

## Code

```python
import pandas as pd


def patch_customers(old, fixes):
    base = old.set_index("customer_id")
    base.update(fixes.set_index("customer_id"))
    return base.reset_index()[list(old.columns)]
```

## Complexity

O(n + m) with hash look-ups on the index.

## Another way

`fixes.set_index("customer_id").combine_first(old.set_index("customer_id"))` also prefers the fix and falls back to
the old value, but it returns the **union** of rows and columns (C9 would be added) and sorts the labels. Follow it
with `.reindex(old["customer_id"])[old columns]` to keep only the customers of `old`, in their order.
