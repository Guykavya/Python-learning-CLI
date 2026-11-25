- **Merging the whole orders table.** The result carries `order_id` and `store_id` columns (all missing) and `_merge`.
- **Forgetting `drop_duplicates` in the merge version.** Customers who ordered are repeated; harmless after the filter
  here, but it breaks any count you take in between.
- **`orders[~orders["customer_id"].isin(customers["customer_id"])]`.** That is the other anti-join: orders without a
  customer (the orphans).
- **Keeping the old index labels.** The task asks for `0, 1, 2, ...`.
