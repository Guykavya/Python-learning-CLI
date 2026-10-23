## Hint 1

A `for` loop calls `iter()` once, then `next()` repeatedly. Which exception tells you the data is finished? Where do you catch it?

## Hint 2

Call `iter(iterable)` once before the loop. Inside a `while True`, call `next(it)` in a `try`. On `StopIteration` leave the loop. Count the items as you go.

## Hint 3

```
it = iter(iterable)
count = 0
while True:
    try:
        item = next(it)
    except StopIteration:
        return count
    action(item)
    count += 1
```
