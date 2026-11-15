**Scenario A: CSV, no partitioning.**
Reasons: the auditor uses Excel and has no Python, and Excel opens CSV directly but not Parquet;
2,000 rows is tiny, so Parquet's compression and column pruning would save nothing a person could
notice. One file per month is already the natural "partition".
Risk: CSV has no types, so Excel guesses. It turns order ids or SKUs with leading zeros into
numbers, may read `2024-06-01` with the local date format, and may show amounts as floats.
Avoid it by writing UTF-8 with a header, amounts as text with exactly two decimals (`19.90`),
ISO dates in UTC, and a short note listing each column and its meaning. Never include customer
emails unless the auditor really needs them.

**Scenario B: Parquet, partitioned by order date (day, or month if days are small).**
Reasons: Parquet is columnar, so a query that needs 4 of 30 columns reads only those columns
instead of the whole 9 GB row by row; it is compressed and keeps types (Decimal amounts,
UTC timestamps), so no query re-parses text. Partitioning by `order_date` matches the filter
of almost every query: "last 7 days" opens 7 folders out of about 1,100 and skips the rest.
About 45,000 rows per day gives files of a healthy size.
`customer_id` is the wrong key: queries do not filter by customer, so nothing is pruned, and
with hundreds of thousands of customers you get hundreds of thousands of folders with a few rows
each (the small-files problem), so listing and opening files costs more than reading them.
Risk: late updates to old orders. Rewrite only the affected day partitions (partition
overwrite) so a re-run never duplicates a day, and keep one explicit schema for every file.

**Scenario C: Parquet (or even CSV), no partitioning, or at most one file per year.**
Reasons: 200 readings a day for 5 years is about 365,000 rows: a few megabytes, which any tool
reads in well under a second, so pruning saves nothing. One Parquet file per year (5 files) keeps
the types and is easy to append to by rewriting only the current year.
The `date/hour` idea creates about 1,800 × 24 = 43,800 folders, each with a file of around 8 rows.
Every file has its own footer and metadata, so the overhead is larger than the data, and a
query for one month must open 720 files instead of 1. Partitions must be big enough to be worth
skipping.
Risk: copying a layout "because the big datasets do it". Choose the key from the queries and the
size: partition only when a partition holds many megabytes and the queries filter on that key.
