# Top 3 products per category

Chapter sections 5.3 and 5.4. "Top N per group" is a question of **order inside groups**: sort, then take the first
N rows of each group. The parts that break real reports are the details: what happens with **ties**, and with a group
that has fewer than N members.

Write `top_products(lines, products, n=3)`.

- `lines` has one row per order line: `order_id`, `product_id`, `qty`, `unit_price`. A product's revenue is the sum
  of `qty * unit_price` over its lines.
- `products` has `product_id` (unique), `category`, `list_price`. Every product in `lines` is in `products`.
- Return the `n` products with the highest revenue in **each category**, as a frame with columns `category`,
  `product_id`, `revenue`, `rank` (an integer, 1 for the best in its category).
- **Ties** in revenue are broken by `product_id` (the smaller id ranks first). So the ranks in a category are always
  `1, 2, ..., k` with no repeats.
- A category with fewer than `n` sold products shows all of them. Products that never sold do not appear.
- Rows sorted by `category`, then `rank`; index `0, 1, 2, ...`. Do not change the inputs.

## Example

```python
import pandas as pd

products = pd.DataFrame({"product_id": ["P1", "P2", "P3", "P4"],
                         "category": ["home", "home", "home", "toys"],
                         "list_price": [10.0, 20.0, 30.0, 5.0]})
lines = pd.DataFrame({"order_id": [1, 1, 2, 3],
                      "product_id": ["P3", "P1", "P2", "P4"],
                      "qty": [1, 2, 1, 4],
                      "unit_price": [20.0, 10.0, 30.0, 5.0]})
print(top_products(lines, products, n=2))
```

```text
  category product_id  revenue  rank
0     home         P2     30.0     1
1     home         P1     20.0     2
2     toys         P4     20.0     1
```

`P1` and `P3` both made 20.0; the tie goes to the smaller id, `P1`, so `P3` is third and falls outside the top 2.
