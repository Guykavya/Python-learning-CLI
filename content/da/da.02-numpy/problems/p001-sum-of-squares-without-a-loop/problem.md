# Sum of squares without a loop

Chapter sections 1.1 to 1.3. Write `sum_squares(n)` that returns

```text
0² + 1² + 2² + ... + (n − 1)²
```

as an **integer**, using NumPy instead of a Python loop.

- `n` is a whole number, `n >= 0`. For `n = 0` and `n = 1` the answer is `0`.
- Return an integer (a Python `int` or a NumPy integer), not a float. `int64` is big enough for every `n` up to `10**6`.
- No Python loop over the numbers: build one array with all of them and let NumPy do the work.

## Example

```python
sum_squares(4)        # 0 + 1 + 4 + 9 = 14
sum_squares(10)       # 285
sum_squares(10**6)    # 333332833333500000
```

## How it is checked

Besides the values, one test calls `sum_squares(10**6)` ten times in a fresh Python process and compares the time
with NumPy doing the same job. A Python loop is several times slower than that and fails with "looks like a Python
loop: vectorise it (Ch. 12.1)".
