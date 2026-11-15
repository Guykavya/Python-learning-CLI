## Hint 1

The rows for `table(240, 46)`: start `r = 240, 46`. The first quotient is `240 // 46 = 5`. The new `r` is `240 - 5*46 = 10`. The new
`s` is `1 - 5*0 = 1`, the new `t` is `0 - 5*1 = -5`. Check: `240*1 + 46*(-5) = 10`.

## Hint 2

The loop stops when `r1` is 0, and the last row printed is that row with `r = 0`. The answer is the row **before** it: that is
what `r0, s0, t0` hold after the final shift.

## Hint 3

For `table(99, 78)` do the divisions: `99 // 78 = 1`, `78 // 21 = 3`, `21 // 15 = 1`, `15 // 6 = 2`, `6 // 3 = 2`... check
each remainder: 21, 15, 6, 3, 0. Keep `s` and `t` as you go, and at the end check `99*x + 78*y = 3`.
