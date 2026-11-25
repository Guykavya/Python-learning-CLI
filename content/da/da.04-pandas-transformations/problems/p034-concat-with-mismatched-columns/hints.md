## Hint 1

Stacking: write down the **union** of the column names, in order of first appearance. Each row has a value only in
the columns its own table had. `join="inner"` keeps only the columns **every** table has.

## Hint 2

```text
c: rows 1,2 (from a) and 3 (from b); columns id, qty, price
   missing cells: price of rows 0 and 1, qty of row 2  -> 3
i: only "id" is common -> 3 rows, 1 column
s: axis=1 aligns on the index: union of labels p, q, r
   x has p, q -> r is NaN;  y has q, r -> p is NaN; a column with NaN is float
```
