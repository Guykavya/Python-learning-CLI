## Hint 1

The `drop` lines come **before** the state line of the same `r`, because the `while` loop runs before the `print`.
At `r = 2` in `pwwkew`, `seen = {p, w}` and `s[2] = w`. The first character to leave is `s[0]`. Is `w` still inside
after that?

## Hint 2

The `while` keeps dropping from the left until the **old copy** of `s[r]` has left. For the second `w` that means
dropping `p` and then `w`, so `l` ends at 2. In `dvdf`, the second `d` only needs the first `d` to leave: `l`
becomes 1 and `v` stays.

## Hint 3

`best` never goes down. In `abba`, after `r = 2` the window is just `b` (length 1) but `best` stays 2. At `r = 3`
the set is `{b}`, so `a` enters without any drop.
