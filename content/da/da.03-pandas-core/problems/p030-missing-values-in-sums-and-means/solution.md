## Approach

`s` has two usable values, 1 and 3. `sum` is `4.0`, the mean is `4 / 2 = 2.0` (the divisor is the count, not the length), `count` is `2`. With `min_count=1` there is at least one real value, so the sum is still `4.0`. With `skipna=False` the missing value is included and poisons the result: `nan`.

`e` has no usable values. The sum of nothing is `0.0` (the neutral element), unless you demand `min_count=1`, which then gives `nan`. The mean of nothing is `0 / 0`: `nan`. `count` is `0`.

`np.nan == np.nan` is `False`: `nan` is "not a number" and does not equal itself, so `(s == np.nan)` is False everywhere. The right test is `isna()`, which marks only the second value.

## Code

The expected output is in `expected.txt`, produced by running the program (pandas 3.1.1).

## Complexity

All of these are O(n) passes.

## Another way

`s.sum() / s.count()` is the mean by hand. If "no data" must not look like "zero", use `min_count=1` (the sum of an empty column becomes missing instead of a false zero).

## Note

The default `sum` of `0.0` for an all-missing column is a classic source of quiet errors: a store with no data looks like a store with zero sales.
