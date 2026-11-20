## Approach

| # | Columns that narrow the search | Result |
|---|---|---|
| 1 | `customer_id =`, `status =`, `created >` | full |
| 2 | `customer_id =`, `status =` (no `created` given) | partial |
| 3 | `customer_id =` | partial |
| 4 | first column missing | no |
| 5 | `customer_id =`; `status` missing, so `created` cannot be used | partial |
| 6 | first column missing | no |
| 7 | `customer_id =`, `status >` (range); `created` after a range is only filtered | partial |
| 8 | `customer_id IN (...)` behaves like several `=`; `status =`; `created >` | full |

These answers were confirmed by running `EXPLAIN QUERY PLAN` on each clause. Clause 1 gives `SEARCH orders USING INDEX idx (customer_id=? AND status=? AND created>?)`; clause 5 gives `SEARCH ... (customer_id=?)`; clause 4 gives `SCAN orders`.

## Complexity

Not applicable.

## Another way

Think of a phone book sorted by last name, then first name, then city: you can look up by last name, or last and first name, but not by first name alone.

## Why it matters

The order of columns in a composite index is the most important design choice about it. Equalities first, then at most one range column, and the columns your queries start with.
