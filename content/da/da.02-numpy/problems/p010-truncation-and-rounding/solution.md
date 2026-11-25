## Approach

Line by line:

1. `astype(int)` truncates towards zero: `2.5 → 2`, `3.5 → 3`, `-1.7 → -1`, and `1e10` fits easily in `int64` → `10000000000`. dtype `int64`.
2. `np.round` sends exact halves to the even neighbour: `0.5 → 0.0`, `1.5 → 2.0`, `2.5 → 2.0`, `-0.5 → -0.0`. The result is still `float64`, and the float `-0.0` prints with its sign.
3. Round first, then convert: `[2.0, 4.0, -2.0, 1e10]` → `[2, 4, -2, 10000000000]`.
4. `floor(-1.7)` goes down to −2, `ceil(-1.7)` up to −1, `int(-1.7)` towards zero: −1.
5. `2.675` cannot be stored exactly; the nearest float is a little **below** 2.675. Python's `round(2.675, 2)` works with that exact stored value and gives `2.67`. `np.round(v, 2)` is faster and simpler: it computes `v * 100`, rounds half to even, and divides by 100. But `2.675 * 100` rounds (in float64) to exactly `267.5`, a half, which goes to the even `268`, so NumPy gives `2.68`. (The first hand-trace of this problem, by its author, said `2.67` for both; running the code showed NumPy's `2.68`. Neither is "wrong": rounding a binary float to decimal places is approximate.)

## Code

The expected output is in `expected.txt`, produced by running the program above.

## Complexity

Not applicable.

## Another way

If a report really needs "half up" for money, work in whole cents (integers) or with Python's `decimal` module, and say which rule you used. For data analysis, half-to-even is preferred because it does not push totals upwards on average.
