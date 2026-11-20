## Hint 1

Lazy: one statement for the orders, then one statement **per order** when `order.lines` is first read. Count the rows each statement returns: 4 orders; then 0, 1, 2, 3 lines.

## Hint 2

`joinedload` puts the lines in the same statement with a `LEFT OUTER JOIN`: every (order, line) pair is a row, and an order with no lines still gives one row (with `NULL` line columns). Count the rows: 1 + 1 + 2 + 3.

## Hint 3

`selectinload`: one statement for the orders (4 rows) and one `SELECT ... WHERE order_id IN (1, 2, 3, 4)` for the lines (6 rows): 2 statements, 10 rows.
