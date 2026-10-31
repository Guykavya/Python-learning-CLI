## Approach

Track the counters through each call:

| Call | setup | stmt | Printed |
|---|---|---|---|
| `t.timeit(number=5)` | 1 | 5 | `1 5` |
| `t.repeat(repeat=3, number=4)`: 3 timings | 1 + 3 = 4 | 5 + 12 = 17 | `3 4 17` (3 timings in the list) |
| `t.timeit(number=0)`: setup still runs, loop runs 0 times | 5 | 17 | `5 17` |

The string examples share the list `data` through `globals=globals()`. The setup `data.clear()`
runs at the start of each timing, then the statement appends the current length:
`timeit(number=3)` gives `[0, 1, 2]`. `repeat(repeat=2, number=2)` clears and appends twice, two
times over; only the last timing's `[0, 1]` is left.

`timeit` disables the garbage collector for the timed loop, so the first lambda records
`False, False`. The second timing's setup calls `gc.enable()`, so its single call records
`True`. After `timeit` returns, the collector is back on: `True`.

Finally `timeit.timeit(stmt, number=2)` returns the elapsed time as a `float` and runs `stmt`
twice more: 19.

## Output

```text
1 5
3 4 17
5 17
[0, 1, 2]
[0, 1]
[False, False, True] True
float 19
```
