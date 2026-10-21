## Hint 1

Make a table with columns `a`, `b`, `a % b`. The line is printed **before** the pair is updated.
How many times does each loop print before `b` becomes 0?

## Hint 2

`a, b = b, a % b` computes both right-hand values first, using the old `a` and `b`, then assigns them.
So `252, 105` becomes `105, 252 % 105`, and `252 % 105` is `42`.

## Hint 3

When `a < b`, `a % b` is just `a` (for example `18 % 48 == 18`). So the first step turns `18, 48` into `48, 18`:
the numbers swap, and the algorithm carries on as normal.
