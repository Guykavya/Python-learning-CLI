## Hint 1

For every `query(...)` call, ask the questions in the order the function asks them: is the view
in this role's set in `GRANTS` (a role missing from `GRANTS` gets the empty set)? If yes, does the
view **have** the requested columns (a view only has the columns its `SELECT` lists)? If yes,
which rows does the view's `WHERE` keep, based on the table **as it is right now**?

## Hint 2

Write the two views out as small tables on paper first.

```
support_orders: id, status, city, email (masked)     -> all 3 rows
analyst_orders: id, customer_key, city, status, amount_cents  -> rows whose status != 'cancelled'

query(role, view, columns, rest):
    view not granted          -> "DENIED role -> view"
    column not in the view    -> "ERROR no such column: <name>"
    else                      -> (list of column names, list of row tuples)

masked email = first letter + '***@' + everything after the '@'
after the UPDATE, re-read the analyst view: a view is a query, not a copy
writing to a view (DELETE/UPDATE/INSERT) -> "cannot modify <view> because it is a view"
```
