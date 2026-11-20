## Approach

```python
INDEX = "CREATE INDEX idx_orders_customer_created ON orders(customer_id, created)"

QUERY = """
SELECT id, created FROM orders
WHERE customer_id = ?
ORDER BY created DESC, id DESC
LIMIT 20
"""
```

The query reads only `customer_id` (filter), `created` (sort and output) and `id` (output; it is the rowid, which SQLite stores in every index entry). So the index contains everything: the plan says `SEARCH orders USING COVERING INDEX idx_orders_customer_created (customer_id=?)`. Inside one customer the entries are sorted by `created`, and equal `created` values by rowid, so reading the index **backwards** gives `created DESC, id DESC` with no sorting step, and `LIMIT 20` stops after 20 entries.

Example: for customer 7 with 5,000 orders, SQLite touches 20 index entries, not 5,000 rows.

## Complexity

`O(log n + 20)` instead of `O(orders of the customer * log)` with a sort.

## Another way

Without the right index the plan shows `USE TEMP B-TREE FOR ORDER BY`: SQLite collects every order of the customer and sorts them. Selecting `*` instead of `id, created` would defeat the covering index (the table has to be read).

## Why it matters

A "latest N" list is a query you run on every page load. An index that matches the filter **and** the sort turns it from a sort of thousands of rows into a read of N entries.
