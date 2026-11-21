## Hint 1

Compute the two numbers of the formula separately first: how many minutes does the task take over `years` years, and how many minutes will the script cost over the same years? Only then compare. Which comparison operator makes a tie come out `False`?

## Hint 2

```text
if any argument < 0 or years < 1: raise ValueError
saved = minutes_per_run * runs_per_year * years
cost  = minutes_to_build + minutes_to_maintain_per_year * years
return saved > 2 * cost, saved
```
