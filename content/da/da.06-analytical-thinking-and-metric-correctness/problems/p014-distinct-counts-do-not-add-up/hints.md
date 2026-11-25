## Hint 1

First decide which rows are in the quarter: the filter is half-open, so check the last row against `< 2025-04-01`. Then list the customers of each month as a set.

## Hint 2

```text
quarter = rows from 1 Jan up to, not including, 1 Apr   (the 1 April 00:00 row is out)
January customers  = {...}   February = {...}   March = {...}
per_month list = sizes of the three sets, in month order
sum = their total;  whole quarter = size of the union
last lines: rows in the quarter, rows in the table, sum minus quarter distinct
```
