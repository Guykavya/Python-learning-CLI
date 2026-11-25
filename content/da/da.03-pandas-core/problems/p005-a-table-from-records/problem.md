# A table from records

Chapter sections 3.2 and 10.2. An API gives you a list of dictionaries, one per order. Some dictionaries lack a key.

Write `orders_frame(records)` that returns a DataFrame with exactly these columns, in this order:

| column | dtype |
|---|---|
| `order_id` | `int64` |
| `customer` | text (`str`) |
| `order_date` | a datetime column (`datetime64`), `NaT` when missing |
| `qty` | `Int64` (nullable integer; missing stays `<NA>`) |
| `price` | `float64` (missing stays `NaN`) |

A key that is absent in a record becomes a missing value in that cell. Dates come as text like `"2024-03-05"`. An empty list gives
an empty table with the same columns. The input list is not changed.

## Example

```python
records = [
    {"order_id": 1, "customer": "Asha", "order_date": "2024-03-05", "qty": 2, "price": 9.5},
    {"order_id": 2, "customer": "Ben", "price": 4.0},
]
df = orders_frame(records)
df.columns.tolist()    # ['order_id', 'customer', 'order_date', 'qty', 'price']
df["qty"].tolist()     # [2, <NA>]
df["order_date"].isna().tolist()   # [False, True]
```
