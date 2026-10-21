## Walkthrough

| i | j | what happens |
|---|---|---|
| 1 | 1 | `continue` (j == i) |
| 1 | 2 | prints `1 2` |
| 1 | 3 | prints `1 3` (sum 4) |
| | | `row 1 done` |
| 2 | 1 | prints `2 1` |
| 2 | 2 | `continue` |
| 2 | 3 | sum 5: `stop inner at 2 3`, break |
| | | `row 2 done` |
| 3 | 1 | prints `3 1` |
| 3 | 2 | sum 5: `stop inner at 3 2`, break |
| | | `row 3 done` |

The `break` stops only the inner loop. The outer loop goes on, and `row ... done` prints
every time.

The second part runs the inner block 2 x 3 = 6 times. `a` ends as `b`, and `b` as `z`.
