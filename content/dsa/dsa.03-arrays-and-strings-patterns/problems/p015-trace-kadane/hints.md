## Hint 1

The first line is printed before the loop: all three values are `a[0]`. For `x = -3`: `cur + x = 2 - 3 = -1`, and
`max(-3, -1) = -1`.

## Hint 2

For `x = 4`: `cur + x = -1 + 4 = 3`, but `x` alone is 4, so `cur` starts fresh at 4. `best` only changes when `cur`
beats it.

## Hint 3

For `x = 3` at the end: `cur` was 0, so `cur + x` and `x` are both 3. In the second list, `cur` keeps restarting
because adding a negative run never helps.
