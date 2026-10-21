## Walkthrough

| Label | Range | Values of `i` | Why | Line printed |
|---|---|---|---|---|
| A | `range(5)` | 0, 1, 2, 3, 4 | one argument means start 0, stop 5 (excluded) | `A: 0 1 2 3 4` |
| B | `range(1, 5)` | 1, 2, 3, 4 | starts at 1, still stops before 5 | `B: 1 2 3 4` |
| C | `range(2, 10, 3)` | 2, 5, 8 | the next value, 11, is past 10, so it stops; 10 is never hit | `C: 2 5 8` |
| D | `range(10, 0, -3)` | 10, 7, 4, 1 | negative step counts down while the value is > 0; the next, -2, is not | `D: 10 7 4 1` |
| E | `range(5, 1)` | none | step is +1, but 5 is not less than 1, so the range is empty | `E: (nothing)` |
| F | `range(0, 10, 4)` | 0, 4, 8 | prints `i * i`, so 0, 16, 64 | `F: 0 16 64` |

For `E`, the label is printed with `end=" "`, the loop body never runs, and then `print("(nothing)")` finishes
the same line.

For `G`, trace the loop:

| Iteration | `i` | `count` after |
|---|---|---|
| 1 | 3 | 1 |
| 2 | 1 | 2 |
| 3 | -1 | 3 |
| 4 | -3 | 4 |

The next value would be -5, which is not greater than -4, so the loop stops. `i` keeps its last value, -3.
Printed: `G: 4 -3`.

## Key idea

`range(start, stop, step)` never includes `stop`. It produces `start`, `start + step`, `start + 2*step`, ...
for as long as the value is still on the near side of `stop` (below it for a positive step, above it for a
negative step). It does not have to land on `stop` exactly. If `start` is already on the far side, the range
is empty and the loop body never runs. With a negative step you must make `start` bigger than `stop`.
