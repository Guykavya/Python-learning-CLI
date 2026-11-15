## Hint 1

`show(3)` prints its first line, then the whole of `show(2)` runs, and only then its own `up` line. Write `show(3)` on the left of your paper and indent each inner call.

## Hint 2

The lines printed before a recursive call come out on the way **down** (outer call first). The lines after the call come out on the way **back up** (inner call first).
