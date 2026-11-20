# Normalise a flat order export

A shop exports one flat row per order line:

```python
{"order_ref": "A-1", "order_date": "2026-01-05", "customer_email": "asha@x.com", "customer_name": "Asha",
 "product_sku": "TEA", "product_name": "Green Tea", "price_paise": 25000, "qty": 2}
```

Write `normalise(rows)` returning a dict of four **tables** (lists of dicts):

| Table | Columns | One row per |
|---|---|---|
| `customers` | `id`, `email`, `name` | distinct `customer_email` |
| `products` | `id`, `sku`, `name`, `price_paise` | distinct `product_sku` |
| `orders` | `id`, `ref`, `date`, `customer_id` | distinct `order_ref` |
| `order_lines` | `order_id`, `product_id`, `qty` | input row |

- Ids are integers `1, 2, 3, ...` in **first-seen order** within each table.
- A customer, product or order that appears on several rows is stored **once** (the first row's values win).
- `order_lines` keeps the input order, one line per input row.
- Joining the four tables back must reproduce every original row (the tests do this).

## Example

Two rows for order `A-1` (tea and coffee) and one row for order `A-2` by the same customer give: 1 customer, 2 products, 2 orders, 3 order lines.
