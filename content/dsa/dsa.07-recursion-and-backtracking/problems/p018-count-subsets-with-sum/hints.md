## Hint 1

Count instead of collecting: each call returns the number of good subsets in its sub-tree. A leaf returns 1 or 0.

## Hint 2

`count(i, remaining) = count(i + 1, remaining - nums[i]) + count(i + 1, remaining)`. What should it return when `i == len(nums)`?

## Hint 3

Pruning: if `remaining == 0` return 1 at once (all other numbers must be left out); if `remaining < 0` return 0. Both are valid only because all numbers are positive.
