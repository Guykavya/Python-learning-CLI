## Hint 1

Write a function `goes_first(x, y)` that tells whether record `x` may stay before record `y`. How do the rules combine: which rule is consulted first, and when do you move on to the next?

## Hint 2

Loop over the rules: if the field values differ, the answer is decided by this rule and the direction (`x < y` for `asc`, `x > y` for `desc`). If all rules are equal, return `True` (keep the left record first: stability).

## Hint 3

Merge sort with `if goes_first(left[i], right[j])` take left, else take right. On a tie `goes_first` is `True`, so the left element wins and the sort is stable.
