## Hint 1

Rows 0 to 3 have nothing to copy (`r` is small): expand from scratch. The `b` at `i = 3` grows to radius 3 (`#a#b#a#` in `t`, which is `aba`), so `(c, r)` becomes `(3, 6)`.

## Hint 2

`i = 5` is inside `(3, 6)`; its mirror is `2 * 3 - 5 = 1`, with `p[1] = 1`, and `r - i = 1`: start 1. Then compare `t[3] = b` with `t[7] = x`. The `x` at `i = 7` is outside every palindrome so far: expand from scratch. How far?

## Hint 3

After `i = 7` the palindrome reaches the end of `t`: `(c, r) = (7, 14)`. Every later row copies from its mirror on the left (`2 * 7 - i`). Can any of them expand further, when `r = 14` is already the last index?
