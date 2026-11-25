- **`size` for orders.** That counts lines; an order with three products would count three times.
- **Summing price and quantity separately and multiplying.** `sum(qty) * sum(unit_price)` is not revenue: each line's
  price must be multiplied by that line's quantity before adding.
- **`lines["revenue"] = ...` on the input.** It adds a column to the caller's frame. Use `assign` or a copy.
- **The dict form without renaming.** Columns come out as `order_id`, `qty`, not `orders`, `units`.
