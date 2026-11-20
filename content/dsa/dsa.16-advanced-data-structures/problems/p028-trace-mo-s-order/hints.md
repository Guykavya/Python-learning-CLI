## Hint 1

Keys: q0 `(0, 4)`, q1 `(1, 8)`, q2 `(0, 3)`, q3 `(0, 7)`, q4 `(1, 6)`. Sorted: q2, q0, q3, q4, q1.

## Hint 2

q2 `[1, 3)` from `[0, 0)`: the right edge grows by 3 (positions 0, 1, 2), then the left edge shrinks by 1 (position 0): 4 steps. The window holds `1, 3`: 2 distinct.

## Hint 3

q0 `[0, 4)` from `[1, 3)`: grow left by 1, grow right by 1. q3 `[2, 7)` from `[0, 4)`: grow right by 3, shrink left by 2. Continue the same way for q4 and q1.
