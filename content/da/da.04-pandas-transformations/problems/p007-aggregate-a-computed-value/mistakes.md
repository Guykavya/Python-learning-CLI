- **Aggregating first and multiplying after.** `sum(qty) * sum(unit_price) * (1 - mean(discount))` mixes lines that
  belong to different prices; the result is meaningless.
- **Using `list_price` instead of `unit_price`.** The list price is the catalogue price; the line records what was
  actually charged.
- **Merging the whole `products` table.** It works, but brings `list_price` along and clutters the frame; select the
  columns you need.
- **Writing the new column into `lines`.** That changes the caller's frame; `assign` returns a new one.
