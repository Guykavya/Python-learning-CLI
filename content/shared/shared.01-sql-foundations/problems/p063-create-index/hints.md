## Hint 1

For requirement 3, which two columns does the query use, and in which order must they appear in the index so the rows come out sorted? Could this same index also serve requirement 1?

For requirement 2: one column is compared with `=`, the other with `>=`. Which should come first in the index?

## Hint 2

```
CREATE INDEX ... ON orders(customer_id, ordered);
CREATE INDEX ... ON orders(status, ordered);
CREATE UNIQUE INDEX ... ON customers(email);
```

Then run `EXPLAIN QUERY PLAN` on each of the three queries in Python and read the last column of each row.
