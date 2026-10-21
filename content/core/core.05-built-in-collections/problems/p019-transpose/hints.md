## Hint 1

Row `i` of the transpose is column `i` of the original. How do you collect a column?

## Hint 2

Column `i` is `[row[i] for row in m]`. Do that for every `i` in `range(c)`.

## Hint 3

`t = [[row[i] for row in m] for i in range(c)]`. The outer comprehension makes the rows of `t`.
