## Hint 1

Which event should you commit to first, so that the most room is left for the others? Not the one that **starts** first and not the **shortest** one: chapter section 4 breaks both. The event that **frees the hall earliest** is safe.

## Hint 2

After sorting by end time you only need one number from the past: `last_end`, the end of the last event you took. An event fits exactly when its start is `>= last_end`. Start `last_end` at `float("-inf")` so the first event always fits.

## Hint 3

```
count = 0
last_end = -infinity
for (s, e) in intervals sorted by (end, start):
    if s >= last_end:
        count += 1
        last_end = e
return count
```
