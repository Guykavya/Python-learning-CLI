# Nested JSON to a table

Chapter section 6.3. An API returns orders. Each order has a customer (a nested object) and a **list** of items. You want one
table row per **order line** (per item), with the order's id and the customer's name repeated on each of its lines.

Write `orders_from_json(records)` using `pd.json_normalize`. The result has exactly these columns, in this order:

| column | meaning |
|---|---|
| `id` | the order id, `int64` |
| `customer` | the customer's `name` (text) |
| `sku` | from the item |
| `qty` | from the item |

Rules:

- an order with several items gives several rows, in the order of the input; an order with an empty `items` list gives no rows;
- a missing nested key (an item without `qty`, an order without a `customer` or without a `name`) becomes a missing value
  in that cell, never an error;
- the index is `0, 1, 2, ...`; the input is not changed.

## Example

```python
records = [
    {"id": 1, "customer": {"name": "Asha"}, "items": [{"sku": "A", "qty": 2}, {"sku": "B"}]},
    {"id": 2, "items": [{"sku": "A", "qty": 5}]},
]
orders_from_json(records)
#    id customer sku  qty
# 0   1     Asha   A  2.0
# 1   1     Asha   B  NaN
# 2   2      NaN   A  5.0          (pandas 3.1.1)
```
