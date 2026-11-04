## Hint 1

Which interval should you keep first if you want to leave the most room for the others?

## Hint 2

The one that **ends earliest**: it blocks the least. Sort by end, keep an interval if its start is `>=` the end of the last kept one, otherwise count it as removed.

## Hint 3

```
intervals.sort(key=lambda x: x[1])
last_end = -infinity; kept = 0
for l, r in intervals:
    if l >= last_end: kept += 1; last_end = r
answer = n - kept
```
