# Do the segments mean anything?

Chapter section 5.4. A segmentation is only useful if it **predicts** something. Build the segments as of a date `T`, then look at what the customers do **after** `T`.

Write `future_value_by_segment(rfm, orders_after)`:

- `rfm`: DataFrame indexed by `customer_id` with a column `segment` (built as of `T`);
- `orders_after`: orders **after** `T` with `customer_id` and `amount` (customers may appear several times, or not at all);
- return a DataFrame indexed by `segment` with the columns `customers` (int), `bought_again_pct` (share of the segment's customers with at least one later order, in percent) and `future_spend_per_customer` (total later spend of the segment divided by its **number of customers**);
- customers with **no** later orders count in the denominator with spend 0 (do not drop them);
- sort the rows by `future_spend_per_customer`, largest first; later orders of customers who are not in `rfm` are ignored.

## Example

Segment A has customers 1, 2, 3 and only customer 1 buys later (two orders, 100 and 50): `customers = 3`, `bought_again_pct = 33.3`, `future_spend_per_customer = 50.0`.
