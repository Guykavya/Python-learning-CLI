## Hint 1

`items()` gives `(key, value)` pairs. `enumerate` gives `(index, item)` pairs, and here each
item is itself a pair.

## Hint 2

In `for tag, *nums in records`, `nums` is always a list.

## Hint 3

Assigning to a loop variable (`first = first * 10`) only moves that name. Changing `row[0]`
changes the list the row refers to.
