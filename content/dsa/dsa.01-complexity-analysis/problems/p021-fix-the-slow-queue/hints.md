## Hint 1

Go through the loop body line by line and write the cost of each line next to it. Watch for operations that look
like one step but hide a loop: which list operations move or scan many items?

## Hint 2

`queue.pop(0)` removes the first item, so every other item must move one place left: O(n) each time.
`user in seen` with a list compares against every stored user: O(number of users).

## Hint 3

You never need to remove items from the log: a `for user in queue:` loop visits them in the same order. And `seen`
only answers "visited before?", which is a job for a set. With a set, `len(seen)` still gives the number of users.
