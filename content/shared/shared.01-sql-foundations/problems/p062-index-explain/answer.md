# Model answer

**1. SCAN vs SEARCH.** `SCAN orders` means SQLite reads all 2 million rows and checks each `customer_id`: work grows with the table (O(n)). After
`CREATE INDEX idx_orders_customer ON orders(customer_id)` the plan says `SEARCH ... USING INDEX`. The index is a sorted B-tree of (customer_id, rowid) pairs. SQLite descends the tree
in about 20 steps to the first row with customer 7, then reads the few matching entries and fetches those rows (O(log n + k)). The second query used
`SEARCH ... USING INTEGER PRIMARY KEY` for the same reason: the primary key is the table's own sorted structure.

**2. Why the scans remain.** The index is sorted by the *raw* value of `customer_id`. `customer_id + 0` and `substr(ordered, 1, 7)` are new values the index never stored, so the
planner cannot use the order and must compute the expression for every row. Rewrite the predicate to compare the bare column (`ordered >= '2024-03-01' AND ordered < '2024-04-01'`) or create an expression index.

**3. Removing the temp sort.** An index on `(customer_id, ordered)`. Inside it, all entries for customer 7 are next to each other and already sorted by `ordered`, so the rows come out in the
requested order and `USE TEMP B-TREE FOR ORDER BY` disappears. Since the query only needs `order_id` (the rowid, which is stored in every index entry), the plan even becomes a `COVERING INDEX`: the table itself is not touched.
This index also serves `WHERE customer_id = ?` alone, so `idx_orders_customer` becomes redundant.

**4. Costs and limits.**
- Every `INSERT`, `UPDATE` of an indexed column and `DELETE` must also update the index (slower writes).
- Indexes take disk space and memory; many indexes can cost more than they save.
- An index does not help `SELECT COUNT(*) FROM orders` (it has to count everything) or a query that returns half the table: reading half the rows through an index is slower than one sequential scan.

| query | plan before | plan after (customer_id, ordered) |
|---|---|---|
| `WHERE customer_id = 7` | SCAN orders | SEARCH ... USING INDEX (customer_id=?) |
| same + `ORDER BY ordered` | SCAN + TEMP B-TREE | SEARCH ... COVERING INDEX, no sort |
