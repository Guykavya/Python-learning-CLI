## Walkthrough

| `i` | `j` | `i + j` | even? | action | `count` | printed |
|---|---|---|---|---|---|---|
| 1 | 1 | 2 | yes | `continue` | 0 | |
| 1 | 2 | 3 | no | count, print | 1 | `1 2` |
| 1 | 3 | 4 | yes | `continue` | 1 | |
| 1 | - | | | inner loop ended, no break, inner `else` | 1 | `row 1 done` |
| 2 | 1 | 3 | no | count, print | 2 | `2 1` |
| 2 | 2 | 4 | yes | `continue` | 2 | |
| 2 | 3 | 5 | no | count, print | 3 | `2 3` |
| 2 | - | | | inner `else` | 3 | `row 2 done` |
| 3 | 1 | 4 | yes | `continue` | 3 | |
| 3 | 2 | 5 | no | count, print | 4 | `3 2` |
| 3 | 3 | 6 | yes | `continue` | 4 | |
| 3 | - | | | inner `else` | 4 | `row 3 done` |
| 4 | 1 | 5 | no | count, print | 5 | `4 1` |
| 4 | 2 | 6 | yes | `continue` | 5 | |
| 4 | 3 | 7 | no | count, print | 6 | `4 3` |
| 4 | - | | | inner `else` | 6 | `row 4 done` |
| 5 | - | | | `i == 5`: print, `break` the outer loop | 6 | `stop at 5` |
| - | - | | | outer `else` skipped (the loop was broken) | 6 | |
| - | - | | | after the loops | 6 | `count 6` |

Full output:

```
1 2
row 1 done
2 1
2 3
row 2 done
3 2
row 3 done
4 1
4 3
row 4 done
stop at 5
count 6
```

## Key idea

- `continue` skips the rest of one pass. The loop carries on, and it still counts as finishing normally,
  so the inner `else` runs every time (`row i done` appears for all four rows).
- `break` leaves the loop at once, and the loop's `else` is skipped. That is why `all rows done` never appears.
- `break` and `continue` only affect the **innermost** loop they are in. The `break` here is in the outer loop
  (it is not inside `for j`), so it ends the outer loop.
- The last `print` is outside both loops and always runs.
