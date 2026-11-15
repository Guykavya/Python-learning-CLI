## Hint 1

Suppose the best run ending at the previous element has a negative sum. Would you ever want to glue it to the front of
the next element?

## Hint 2

`cur = max(x, cur + x)`: start over when the old run only hurts. Track the largest `cur` ever seen in `best`. Start
both at `a[0]`, not at 0, so that an all-negative array works.

## Hint 3

```
cur = best = a[0]
for x in a[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)
print best
```
