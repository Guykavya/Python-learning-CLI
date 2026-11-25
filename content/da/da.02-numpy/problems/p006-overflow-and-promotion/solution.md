## Approach

Since NumPy 2 (NEP 50) the result dtype depends on the **types**, not the values, and a Python number is "weak": it takes the array's dtype if it can.

1. `px + 100`: `100` fits in `uint8`, so the result is `uint8` and wraps: 300 − 256 = 44 and 350 − 256 = 94. No warning: arrays never warn about integer overflow (Ch. 4.2).
2. `px + 300`: `300` cannot be a `uint8` at all, so NumPy refuses with `OverflowError` before computing anything.
3. `px + np.int64(100)`: a NumPy scalar is "strong"; `uint8` and `int64` promote to `int64`, which holds 300 and 350.
4. `px + 2.5`: an integer type cannot hold a fraction, so the result is `float64`: 202.5 and 252.5.
5. `float32 + 1.5`: the weak Python float adapts to `float32`; 2.5 and 3.5 are exact in `float32`.

## Code

The expected output is in `expected.txt`, produced by running the program above with NumPy 2.

## Complexity

Not applicable: the lesson is about types.

## Another way

`np.result_type(px, 100)` and `np.result_type(px, np.int64(100))` answer the dtype question without computing anything. In real code, widen first (`px.astype(np.int16)`) and clip (p007).
