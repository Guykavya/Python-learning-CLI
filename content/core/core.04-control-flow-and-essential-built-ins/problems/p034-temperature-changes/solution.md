## Approach

Neighbour pairs with `zip(temps, temps[1:])`, day numbers with `enumerate(start=2)`, and a
"best so far" for the biggest rise.

## Code

```python
temps = input().split()
if len(temps) < 2:
    print("Not enough data")
else:
    best = 0
    best_day = 0
    for day, (before, after) in enumerate(zip(temps, temps[1:]), start=2):
        change = int(after) - int(before)
        shown = f"{change:+d}" if change else "0"
        print(f"Day {day}: {shown}")
        if change > best:
            best = change
            best_day = day
    if best > 0:
        print(f"Biggest rise: +{best} on day {best_day}")
    else:
        print("No rises")
```

## Why start `best` at 0

We only care about **rises**, which are above 0. Starting at 0 means falls and no-change days
never become the best, and "no rise found" is simply `best == 0`.

## Why `>` and not `>=`

With `>=`, a later tie would replace the earlier day. The task wants the earliest.
