## Hint 1

The root call prints `'' 0 0`. Only `(` is allowed. In the child `'(' 1 0` both branches are allowed: first `(`, then `)`.

## Hint 2

When `opened == n`, only `)` remains possible until `closed == opened`. A call whose string has length `2n` records it and returns.

## Hint 3

For `n = 3` every result starts with `(`. Among the results, the one with the most `(` at the start comes first, because the `(` branch is always tried first.
