## Hint 1

A `for` loop over a list keeps an internal position: 0, 1, 2, ... It does not remember items,
only the position. What happens to the position when an item before it is removed?

## Hint 2

Write the list and the position on paper for every turn of the first two loops.

## Hint 3

`for v in vals: v = v + 1` rebinds `v` only. `vals[i] = ...` changes the list.
