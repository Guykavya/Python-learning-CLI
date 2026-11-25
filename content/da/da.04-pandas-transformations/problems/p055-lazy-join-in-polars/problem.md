# Lazy join in Polars

Chapter sections 13.4 and 13.6. A lazy query is a **plan**: nothing runs until `collect()`, and the optimiser can
reorder and trim the steps. Build the plan for *the top products of each category*.

Write `top_products_lazy(items, products, n=2)`:

- `items` and `products` are Polars **`LazyFrame`s**. `items` has `order_id`, `product_id`, `qty`, `unit_price`;
  `products` has `product_id`, `category`, `list_price` (one row per product);
- join the lines to their product (an **inner** join, so a line whose product is unknown is left out), declaring the
  many-to-one relationship with `validate="m:1"`;
- `revenue = qty * unit_price` per line, summed per `category` and `product_id`;
- keep the `n` products with the highest revenue in each category (fewer if the category has fewer sold products);
  ties are broken by `product_id` alphabetically;
- return a **`LazyFrame`** (do not call `collect()` yourself) whose collected result has exactly the columns `category`,
  `product_id`, `revenue`, sorted by `category`, then revenue from highest to lowest, then `product_id`.

Polars' `group_by(...)` has `head(n)`, like pandas: after sorting, `group_by("category", maintain_order=True).head(n)`
keeps the first `n` rows of each category. The tests check the type, then compare the collected result with pandas.

## Example

```python
import polars as pl

items = pl.LazyFrame({"order_id": [1, 1, 2], "product_id": ["P1", "P2", "P1"],
                      "qty": [1, 2, 3], "unit_price": [10.0, 5.0, 10.0]})
products = pl.LazyFrame({"product_id": ["P1", "P2"], "category": ["home", "home"], "list_price": [10.0, 5.0]})
plan = top_products_lazy(items, products, n=1)
print(type(plan).__name__)
print(plan.collect().to_dicts())
```
```text
LazyFrame
[{'category': 'home', 'product_id': 'P1', 'revenue': 40.0}]
```
