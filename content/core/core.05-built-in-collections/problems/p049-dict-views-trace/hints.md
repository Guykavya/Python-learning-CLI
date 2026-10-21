## Hint 1

`keys()`, `values()` and `items()` return views, not copies. A view always shows the dict as it
is **now**. `list(...)` makes a snapshot.

## Hint 2

Deleting a key and adding it again puts it at the **end** of the dict's order.

## Hint 3

In `d | other`, the right side wins for shared keys, but a key keeps the position it had in `d`.
`d |= ...` changes `d`, so the views see it.
