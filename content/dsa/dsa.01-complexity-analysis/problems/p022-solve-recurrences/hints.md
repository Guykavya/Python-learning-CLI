## Hint 1

For each `a T(n/b) + n^d`, identify `a` (number of recursive calls), `b` (how much smaller each call is) and `d`
(the exponent of the extra work: `1` is `n^0`, `n` is `n^1`). Then compare `a` with `b^d`.

## Hint 2

For a recursion tree, write the total work on each level. For 4: level 0 has one box doing `n`; level 1 has 4 boxes
doing `n/2` each, total `2n`; level 2 has 16 boxes doing `n/4` each, total `4n`. How many levels, and which one is
biggest?

## Hint 3

For subtract-by-one recurrences, just expand: `T(n) = T(n-1) + n = T(n-2) + (n-1) + n = ...`. For 8, count boxes
per level: 1, 2, 4, ...
