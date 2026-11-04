## Hint 1

Imagine walking along the time line. At which moments do you learn about a free gap? What do you need to remember to know where the busy part so far ends?

## Hint 2

Sort by start. Keep `busy_until` (initially 0). For each meeting `(l, r)`: the gap is `l - busy_until` (if positive); then `busy_until = max(busy_until, r)`. After the loop add the final gap `T - busy_until`.

## Hint 3

```
meetings.sort(); busy_until = 0; best = 0
for l, r in meetings:
    best = max(best, l - busy_until)
    busy_until = max(busy_until, r)
best = max(best, T - busy_until)
```
