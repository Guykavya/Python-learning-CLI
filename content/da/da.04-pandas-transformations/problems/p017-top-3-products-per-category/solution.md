## Approach

1. Aggregate lines to **one row per product** (revenue = sum of `qty * unit_price`).
2. Attach the category with a one-to-one merge (`validate="1:1"`: one row per product on both sides), so no product is
   duplicated.
3. Sort by category, then revenue **descending**, then product id **ascending**. The third key is the tie rule; without
   it, equal revenues keep whatever order the data happened to have.
4. `groupby("category").head(n)` keeps the first `n` rows of each category, or all of them in a small category.
5. `cumcount() + 1` numbers the kept rows 1, 2, 3 inside each category: unique, integer ranks.

## Code

```python
import pandas as pd


def top_products(lines, products, n=3):
    rev = (lines.assign(revenue=lines["qty"] * lines["unit_price"])
                .groupby("product_id", as_index=False)["revenue"].sum())
    rev = rev.merge(products[["product_id", "category"]], on="product_id", how="left", validate="1:1")
    top = (rev.sort_values(["category", "revenue", "product_id"], ascending=[True, False, True])
              .groupby("category")
              .head(n))
    top = top.assign(rank=top.groupby("category").cumcount() + 1)
    return top[["category", "product_id", "revenue", "rank"]].reset_index(drop=True)
```

## Complexity

O(L) to aggregate L lines, then O(P log P) to sort P products. `head` and `cumcount` are O(P).

## Another way

Rank, then filter (Ch. 5.3, way 3): after sorting by `product_id`, `rank(method="first", ascending=False)` inside each
category gives ties to the earlier (smaller) id; keep `rank <= n`. Or `nlargest` per group, which keeps the first of
ties in data order, so you would still have to sort by id first. The sort + `head` form makes the tie rule visible.
