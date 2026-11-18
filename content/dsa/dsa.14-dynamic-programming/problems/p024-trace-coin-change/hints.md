## Hint 1

Only `f[0]` is a number at the start, and coin 1 always fits, so every `tried` list holds plain numbers (no `inf` is ever printed). For `a = 3` the coins that fit are 1 and 3: `tried = [f[2] + 1, f[0] + 1]`. What are those two numbers?

## Hint 2

`f[a]` starts as `INF`, so the first coin tried always wins and sets `last[a]`. After that a coin replaces it only if its value is **strictly smaller**. At `a = 5` the list is `[f[4] + 1, f[2] + 1, f[1] + 1]`: which positions hold the minimum, and which of them came first?

## Hint 3

The table line prints the whole list `f`, `f[0]` included. The walk back: `a = 6`, take `last[6]`, subtract it, and repeat until `a` is 0. Each step adds one coin to `used`, so `len(used)` must equal `f[6]`.
