## Hint 1

You cannot ask a list for its block size directly, but `sys.getsizeof` grows only when the block
is replaced. So: what do you need to remember between two appends to notice a change? What is
the "previous size" before the very first append? For `copy_cost`, can you reuse
`growth_points`?

## Hint 2

```
growth_points(n):
    lst = []
    previous = getsizeof(lst)
    points = []
    repeat n times:
        lst.append(None)
        size = getsizeof(lst)
        if size != previous:
            points.append(len(lst))
            previous = size
    return points

copy_cost(n) = sum of (p - 1) for p in growth_points(n)
capacity(lst) = (getsizeof(lst) - getsizeof([])) // struct.calcsize("P")
```
