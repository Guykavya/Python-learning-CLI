## Hint 1

What do you need to know about each value before you can rank them? Build that first.

## Hint 2

After counting, sort the distinct values with a key that orders by count descending, then value ascending. A key of `(-count, value)` does both.

## Hint 3

```
count = {}
...
items = sorted(count, key=lambda v: (-count[v], v))
print(*items[:k])
```
