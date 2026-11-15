## Approach

The model answer is in `answer.md`. The decision rules behind it:

| Question | Points to |
|---|---|
| A human opens it in a spreadsheet, the data is small | CSV with documented columns |
| Programs query it, it is large, queries need few columns | Parquet |
| Most queries filter on one column (usually a date) | partition by that column |
| A partition would hold only a few rows | coarser partitions or none at all |

## Check your answer

- A: did you pick CSV because of the **user** (Excel, no Python) and the **size**, not because "CSV is simpler"?
- A: did you name a concrete Excel/CSV trap (leading zeros, date formats, floats for money, encoding) and a fix?
- B: did you mention **column pruning** (reading 4 of 30 columns) and **types/compression**, not only "Parquet is faster"?
- B: did you partition by **order date** because the queries filter on recent days, and say how many partitions a 7-day query opens?
- B: did you explain why `customer_id` fails twice: no query filters on it, and it creates a huge number of tiny folders?
- C: did you compute the size (about 365,000 rows) and conclude partitioning is not worth it?
- C: did you name the **small-files problem** (tens of thousands of files of a few rows, metadata larger than data)?
- Did every reason use the scenario's numbers or users?

## Another way

For B, month partitions (`order_month=2024-06`) are also a good answer: about 1.4 million rows each,
and a 30-day query reads one or two folders. Day partitions prune better for the 7-day
dashboards; month partitions give fewer, larger files. Both are defensible if you say why. For A,
an `.xlsx` export written by a library is also reasonable; it avoids Excel's guessing because the
file carries cell types.
