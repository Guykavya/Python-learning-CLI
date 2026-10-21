## Hint 1

Join the three lines into one 9-character string `b`. Square at row `r`, column `c` is
`b[3 * r + c]`.

## Hint 2

A player `p` wins on row `r` when `all(b[3 * r + c] == p for c in range(3))`. Write the
column and both diagonals the same way, and combine them with `any`.

## Hint 3

Order of checks: shape and characters, counts, then compute `x_wins` and `o_wins`, then the
impossible-winner rules, then the verdicts.
