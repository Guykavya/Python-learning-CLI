## Approach

Compute `days_needed` for each `mid` with the greedy rule, then apply the half-open rule: feasible means `hi = mid`, infeasible means `lo = mid + 1`.

## Expected output

```text
lo 4 hi 16 mid 10 days 2 ok True
lo 4 hi 10 mid 7 days 3 ok True
lo 4 hi 7 mid 5 days 4 ok False
lo 6 hi 7 mid 6 days 3 ok True
answer 6
```

## Why

Start: `lo = 4`, `hi = 16`, `mid = 10`. Capacity 10: `3+2+2 = 7`, adding 4 gives 11 > 10, so day 2 starts with 4, `+1 = 5`, `+4 = 9`: 2 days. Feasible, so `hi = 10`.
`mid = 7`: `3+2+2 = 7` fits, `4` starts day 2 (`4+1 = 5`, `+4 = 9 > 7` so day 3 starts with 4): 3 days, feasible, `hi = 7`.
`mid = 5`: `3+2 = 5`, then `2+... ` day 2 is `2+4 = 6 > 5` so `2` alone, then `4+1 = 5`, then `4`: 4 days, not feasible, `lo = 6`.
`mid = 6`: `3+2`, `2+4`, `1+4`: 3 days, feasible, `hi = 6`. Now `lo == hi == 6`: the answer.
13 candidates (4 to 16) were cut down in 4 probes.
