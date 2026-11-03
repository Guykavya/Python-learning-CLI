- Using `created_at.date()` without converting to UTC first. An order made at 01:30 in India lands in
  the next day's folder while the same instant from another source lands in the previous day: the
  daily totals no longer add up.
- Storing `order_date` inside the files as well. The value is repeated in every row for nothing, and
  reading the dataset with hive partitioning finds the column twice.
- Reading the whole dataset and filtering the Python list afterwards. It gives the right rows on a
  small test, but it opens every file of every day, and one damaged file anywhere breaks every read.
- Forgetting the explicit schema. A day whose cities are all `None` gets a `null`-typed column, and
  the partitions no longer have the same schema.
- Raising an error for a day with no folder. "No orders that day" is a normal answer: `[]`.
- Choosing a partition key with too many values (for example the order id or the exact timestamp).
  You get thousands of folders with one tiny file each: the small-files problem.
