## Hint 1

Keep three numbers on paper: how many orders, what `a["1"]` holds, the counter. Update them after each call, then copy them into the line.

## Hint 2

Call 4 creates `a["1"]` (status `201`), call 5 sets it to the same value (status `200`, state unchanged). Calls 8 and 9: the first deletes (`204`), the second finds nothing (`404`) and changes nothing.

## Hint 3

`POST` adds an order each time (2 orders after call 3). `PATCH` adds to the counter each time (2 after call 7). `PUT` and `DELETE` repeated leave the state as it was after the first call.
