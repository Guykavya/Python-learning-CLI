## Hint 1

Item 0 has weight 3 and value 5. For `w` from 7 down to 3, `g[w - 3]` is still 0 (nothing was taken yet), so every `g[w]` with `w >= 3` becomes `max(0, 0 + 5) = 5`. Capacities 0, 1 and 2 are not touched: the item does not fit.

## Hint 2

Item 1 has weight 1 and value 2. Start at `w = 7`: `g[7] = max(5, g[6] + 2)`, and `g[6]` is still 5 from the item 0 line, so `g[7] = 7`. Continue down to `w = 1`. At `w = 3`: `max(5, g[2] + 2) = max(5, 2) = 5`. Which capacities end up at 7?

## Hint 3

For item 2 (4, 6) and item 3 (2, 3), make a small table per item: one column `w`, one column `old g[w]`, one column `old g[w - weight] + value`, and the max. Use only values from the previous line. For example, item 2 at `w = 7` reads the old `g[3] = 5`: `5 + 6 = 11`.
