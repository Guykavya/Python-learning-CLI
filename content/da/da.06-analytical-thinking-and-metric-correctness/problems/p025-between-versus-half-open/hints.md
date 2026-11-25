## Hint 1

What does `"2025-02-28"` mean as a time of day? Does `between` include its end? For each of the six timestamps, ask two
questions: is it `>= 2025-02-01`, and is it below the end (`<=` the 28th at midnight for `between`, `<` the 1st of
March for the half-open version)?

## Hint 2

```text
t:        Feb 01 00:00 | Feb 14 10:00 | Feb 28 00:00 | Feb 28 15:30 | Feb 28 23:59:59.5 | Mar 01 00:00
closed:   end = Feb 28 00:00, included      -> T, T, T, F, F, F
half-open: start <= t < Mar 01 00:00          -> T, T, T, T, T, F
last_day = from Feb 28 00:00 up to (not including) Mar 01 00:00 -> rows 3, 4, 5
the last line: between(Feb 01, Mar 01) includes Mar 01 00:00 itself -> all six
```
