## Approach

Let pandas do the relationship check (`validate="m:1"`), because it runs **before** the join and cannot be forgotten.
When it fails, find the offending ids yourself: `duplicated()` marks the second and later copies of each id, `unique()`
lists each offender once, `sorted` makes the message stable. `raise ... from err` keeps pandas' original error attached
for debugging. When it passes, the left join keeps exactly one row per line.

## Code

```python
import pandas as pd


def lookup_products(lines, products):
    try:
        return lines.merge(products[["product_id", "category", "list_price"]], on="product_id",
                           how="left", validate="m:1")
    except pd.errors.MergeError as err:
        ids = products["product_id"]
        dups = sorted(ids[ids.duplicated()].unique().tolist())
        raise ValueError(f"duplicated product_id in products: {dups}") from err
```

## Complexity

O(n + p) for the check and the hash join; the duplicate search is O(p).

## Another way

Check before merging: `dups = products["product_id"][products["product_id"].duplicated()]`, raise if not empty, then
merge with `validate="m:1"` as a second line of defence. `pandas.errors.MergeError` is a subclass of `ValueError`, so a
caller who catches `ValueError` catches both forms.
