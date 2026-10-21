## Hint 1

How much work does `max(a)` do? Does its answer change from one pass of the loop to the next?

## Hint 2

Anything that gives the same result on every pass of a loop can be computed once, before the loop. This is
called hoisting it out of the loop.

## Hint 3

```
best = max(a)
for each x in a:
    if x == best: top += 1
    if 2 * x >= best: half += 1
```
