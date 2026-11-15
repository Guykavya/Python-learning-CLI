## Hint 1

Write `total` after each step for `5 -10 3 4`. Which subarray reaches 7? Where does the window's left end stand when
`r` reaches that subarray, and what is inside the window to its left?

## Hint 2

The code drops elements only when `total >= s`. In your example, dropping the left part would make `total`
**bigger**. Which assumption about "dropping makes the sum smaller" is false here?

## Hint 3

For the replacements, think about prefix sums: a subarray sum is `P[j] - P[i]`, and that formula does not care about
signs. Which earlier problem in this module counted subarrays with sum `k` that way?
