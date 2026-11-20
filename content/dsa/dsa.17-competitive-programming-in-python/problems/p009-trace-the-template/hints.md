## Hint 1

`print` writes immediately. `out.append(...)` only stores a string. Nothing from `out` is written until `sys.stdout.write` after the loop.

## Hint 2

Per case, in order: `solve` prints `solving n`, returns the string; `main` appends it. After case 2 it prints `two done`. So before the final block there are four printed lines: `solving 3`, `solving 1`, `two done`, `solving 4`.

## Hint 3

Case results: `[4, 9, 2]` gives `9 1`; `[7]` gives `7 0`; `[5, 5, 8, 8]` gives `8 2` (the first 8 is at index 2). Then the three `Case` lines are written together, and `end` is printed last.
