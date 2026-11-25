## Hint 1

`orders` has one row per order, `lines` has one row per line, and the merge keeps one row per line. Each order's freight is copied to all of its lines: order A has three lines.

## Hint 2

Freight in `flat`: A counted 3 times (30), B twice (40), C once (30). Add them, and divide by 60.
