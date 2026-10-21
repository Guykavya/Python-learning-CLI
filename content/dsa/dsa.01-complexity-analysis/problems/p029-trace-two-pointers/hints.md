## Hint 1

In the first part `j` is **not** reset. It starts at 0 and only ever increases. Make a trace table with columns
`i`, `a[i]`, `j` before, `j` after, `inner`, `pairs`.

## Hint 2

For `i = 0` (`a[i] = 1`): `j` moves past values 1, 2, 4 (differences 0, 1, 3 are less than 4) and stops at 7
(difference 6). So `j = 3`, and `pairs += 3 - 0 - 1 = 2`.

## Hint 3

In the second part, the `while` loop for each `i` runs once for every `j >= i` with `a[j] - a[i] < 4` (including `j = i`
itself). Count those for each `i` and add.
