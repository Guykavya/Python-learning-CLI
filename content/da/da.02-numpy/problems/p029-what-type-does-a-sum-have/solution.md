## Approach

Line by line:

1. `flags.sum()` counts the `True`s: **3**, dtype `int64` (booleans are summed as the default integer).
2. `mean` of integers is always `float64`: 7 / 3 = **2.3333333333333335** (the float nearest to 7/3, printed with Python's shortest repr).
3. `small.sum()`: a `uint8` array is summed in a 64-bit accumulator of the same kind (unsigned), so **300 uint64**. No wrap.
4. `sum(dtype=np.uint8)` forces an 8-bit accumulator: 300 − 256 = **44 uint8**.
5. `cumsum` follows the same rule as `sum`: **[200, 300] uint64**.
6. `small + small` is element-wise: the result stays `uint8` and each element wraps: 400 − 256 = 144, and 200: **[144, 200] uint8**.
7. `int8` summed in `int64`: **200 int64** (an `int8` could only hold up to 127).
8. A `float32` sum stays `float32`: **0.75 float32** (0.75 is exact in binary).

## Code

The expected output is in `expected.txt`, produced by running the program with NumPy 2.5.4.

## Complexity

Not applicable. The lesson: reductions widen small integer types, element-wise operations do not.

## Another way

When unsure, ask NumPy instead of guessing: `np.result_type(small, small)` for an operation, or look at `.dtype` of a small example. For images, convert first (`img.astype(np.int16)` or `float`) before adding, as Ch. 20.3 does.
