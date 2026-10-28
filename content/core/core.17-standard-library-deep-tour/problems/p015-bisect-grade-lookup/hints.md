## Hint 1

`bisect_right(breakpoints, score)` counts how many breakpoints are `<= score`. For score 60 with `[60, 70, 80, 90]` that count is 1. For 59 it is 0. How does "number of breakpoints passed" map to a position in `"FDCBA"`? Which bisect makes a score **equal** to a breakpoint count as passing it?

## Hint 2

For the range: `bisect_left(a, lo)` is the index of the first item `>= lo`. `bisect_right(a, hi)` is the index just after the last item `<= hi`. The items in between are exactly the ones in `[lo, hi]`. What do you get when `lo > hi`?

## Hint 3

```
grade(score, breakpoints, grades):
    return grades[bisect_right(breakpoints, score)]

count_in_range(a, lo, hi):
    if lo > hi: return 0
    return bisect_right(a, hi) - bisect_left(a, lo)
```
