## Hint 1

At `i = 0` nothing is waiting, so there are no pops; index 0 is pushed. At `i = 1`, `x = 1`: is `nums[0] = 2` smaller than 1? Then index 1 is pushed on top of index 0.

## Hint 2

At `i = 2`, `x = 2`: the top is index 1 (value 1), and `1 < 2`, so it is popped and gets the answer 2. Now the top is index 0 (value 2): is `2 < 2`? Equal values are **not** greater, so the loop stops.
