# Length of a vector

Chapter section 1.2. The **length** (norm) of a vector is the square root of the sum of its squared entries: for `[3, 4]` it is `5`.

Write `norm(v)` that returns the length of `v` as a Python `float`. `v` is a list or a NumPy array of numbers. Use a loop (or a sum of squares) and `math.sqrt`. **Do not use `np.linalg.norm`** (the test turns it off).

## Example

```text
norm([3, 4])        ->  5.0
norm([1, 1, 1, 1])  ->  2.0
norm([0, 0, 0])     ->  0.0
```
