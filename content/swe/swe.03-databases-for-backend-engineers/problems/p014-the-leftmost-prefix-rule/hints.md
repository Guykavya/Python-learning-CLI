## Hint 1

Walk the columns from the left. A column can narrow the search only if every column before it was compared with `=` (or `IN`) and it appears in the `WHERE`. Where does the chain break?

## Hint 2

Clause 4 and 6 do not mention `customer_id`: the first column of the index is missing, so the index cannot be entered. Clause 5 has `customer_id` but not `status`: the chain stops after one column.

## Hint 3

Clause 7: `customer_id =` then `status >` (a range): `status` is used, but `created` after a range cannot narrow it. Clause 8: `IN (1, 2)` counts like several equalities, so all three columns are used.
