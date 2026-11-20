## Hint 1

A query is "covered" when every column it needs is in the index. Which columns does the query use: to filter, to sort, to return?

## Hint 2

An index `(customer_id, created)` is sorted by customer, then by `created`. Walking it **backwards** gives the newest first. Where is the `id`? In SQLite every index entry also holds the rowid (and `id` is the rowid).

## Hint 3

```text
INDEX = CREATE INDEX ... ON orders(customer_id, created)
QUERY = SELECT id, created FROM orders WHERE customer_id = ? ORDER BY created DESC, id DESC LIMIT 20
```
