## Approach

The model answer is in `answer.md`. The rule behind all five: pick the format by **who reads it next and what must survive**. CSV is the lowest common denominator (text, readable everywhere, loses types). Parquet is the format for data that machines hand to machines. Excel is for people. JSON is for nested data. A database is for data that already lives there.

## Code

No code: a written explanation. To see why 2 matters, write a small frame with a date and the text `"007"` to CSV and back with `read_csv`, then do the same with `to_parquet` / `read_parquet` and compare the dtypes (Ch. 6.5).

## Complexity

Not applicable. Cost-wise, reading 3 of 40 columns from Parquet touches about 3/40 of the data; CSV must scan everything.

## Another way

You could answer with a table (situation, format, reason). A table is fine, as long as every row has a reason, not just a format name.
