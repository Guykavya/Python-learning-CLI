## Hint 1

For `i = 1` and `i = 2`, only the 1-step fits: each cell copies the one before it. From `i = 3` the 3-step fits too (it reads `f[0]`), and from `i = 4` all three steps fit. Write the three indices `i - 1`, `i - 3`, `i - 4` under each box and cross out the negative ones.

## Hint 2

The terms are printed in the order of `steps = [1, 3, 4]`, so the largest index comes first: `f[i-1]`, then `f[i-3]`, then `f[i-4]`. The printed sum is the cell **after** all its terms were added. The last two lines print the whole list and `f[8]`.
