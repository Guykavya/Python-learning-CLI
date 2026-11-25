# Fill gaps with the group median

Chapter section 4.1. A missing price is better guessed from products **of the same category** than from the whole
catalogue. `fillna` with a `transform` of the group statistic does it in one line. When a whole category has no price,
its median is missing too and the gap stays: report those categories instead of hiding them.

Write `fill_price_by_category(products)`. `products` has columns `product_id`, `category` and `list_price` (float,
some missing), and any index. Return a tuple `(filled, unfilled)`:

- `filled`: a **new** frame with the same rows, order, index and columns, where each missing `list_price` is replaced by
  the **median** list price of its category. Known prices are not changed.
- `unfilled`: the sorted list of categories that have **no** known price at all (their prices stay missing).

Do not change `products`.

## Example

```python
import pandas as pd

products = pd.DataFrame({
    "product_id": ["P1", "P2", "P3", "P4", "P5"],
    "category": ["home", "home", "home", "toys", "toys"],
    "list_price": [100.0, None, 300.0, None, None],
})
filled, unfilled = fill_price_by_category(products)
print(filled["list_price"].tolist())
print(unfilled)
```

```text
[100.0, 200.0, 300.0, nan, nan]
['toys']
```
