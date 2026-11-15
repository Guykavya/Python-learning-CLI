## Hint 1

List the cities of each table on paper, including the NULLs. Then do the four operations one at a time. For each, ask: are duplicates kept?
Are the two NULLs "the same" row here? Finally sort the four result lines by `n` descending, then by the label.

## Hint 2

```
suppliers: Pune, Pune, Delhi, NULL        (4 rows)
customers: Delhi, NULL, Goa, Goa, Mumbai  (5 rows)

union_all  = 4 + 5                       = ?
union      = distinct values overall     = Pune, Delhi, NULL, Goa, ... ?
intersect  = distinct values in BOTH     = ?
except     = distinct values only in suppliers = ?
```
