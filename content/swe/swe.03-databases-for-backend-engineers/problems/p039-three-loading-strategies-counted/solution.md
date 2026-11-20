## Approach

| Strategy | Statements | Rows returned |
|---|---|---|
| lazy | 1 (orders) + 4 (lines of each order) = **5** | 4 + (0 + 1 + 2 + 3) = **10** |
| joinedload | 1 `LEFT OUTER JOIN` = **1** | 1 + 1 + 2 + 3 = **7** (an order with no lines still gives one row; an order with 3 lines gives 3 rows) |
| selectinload | 1 (orders) + 1 (`IN (1, 2, 3, 4)`) = **2** | 4 + 6 = **10** |

The statement counts were confirmed by running the three variants (5, 1 and 2); the row counts follow from the data.

With 400 orders, lazy loading needs 401 statements (the N+1), `selectinload` still needs 2 (the `IN` list is longer; SQLAlchemy splits very long lists into chunks of 500), and `joinedload` still needs 1.

`joinedload` is best for **many-to-one** links (an order's customer: one row each, no repetition) and small collections. For big collections it repeats the parent's columns in every row, which wastes bandwidth.

## Complexity

Not applicable.

## Another way

`subqueryload` and `lazy="select"` are the other strategies; `lazy="raise"` (problem 40) forbids lazy loading so that the mistake becomes an error.

## Why it matters

"Fewer statements" is not always "less data": count both. A single query that returns the same parent a hundred times can be slower than two small ones.
