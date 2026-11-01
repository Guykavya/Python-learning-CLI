## Hint 1

For each container, write its contents as a list after every `put` and `get`. For the
`PriorityQueue`, ask how Python compares two tuples: first elements first, and only if they are
equal, the second elements. Which string is smaller, `"also urgent"` or `"urgent"`?

## Hint 2

For the small queue (`maxsize=2`):

```
put x       -> [x]
put y       -> [x, y]      full
put_nowait z -> no room: raises queue.Full (nothing added)
get_nowait  -> x, now [y]
put_nowait z -> [y, z]
get, get    -> ?
```

And an unbounded queue (`maxsize` 0): can it ever be full?
