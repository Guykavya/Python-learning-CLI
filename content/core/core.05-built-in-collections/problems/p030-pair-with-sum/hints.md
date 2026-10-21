## Hint 1

Walk left to right. At position `j` with value `x`, which earlier value would complete the pair?

## Hint 2

You need `target - x`. Keep a dict from value to the **first** position it appeared.

## Hint 3

Check the dict **before** storing the current number, so a number is not paired with itself.
Only store a value the first time you see it, so you keep the smallest `i`.
