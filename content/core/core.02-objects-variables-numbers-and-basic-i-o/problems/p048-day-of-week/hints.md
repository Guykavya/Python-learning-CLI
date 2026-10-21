## Hint 1

You need a number that is 1 when `m` is 1 or 2, and 0 when `m` is 3 to 12. What is `(14 - m) // 12`
for `m = 1`, `2`, `3` and `12`?

## Hint 2

With `early = (14 - m) // 12`: the adjusted year is `year - early` and the adjusted month is
`m + 12 * early`.

## Hint 3

Zeller gives 0 = Saturday, 1 = Sunday, 2 = Monday. ISO wants 1 = Monday ... 7 = Sunday.
Shift so that Monday (h = 2) becomes 0, wrap with `% 7`, then add 1: `(h + 5) % 7 + 1`.
