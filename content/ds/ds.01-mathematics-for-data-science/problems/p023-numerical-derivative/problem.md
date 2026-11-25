# Numerical derivative

Chapter section 6.2. You can estimate the slope of `f` at `x` without any algebra: take a small step `h` on both sides. The **central difference** `(f(x + h) - f(x - h)) / (2 h)` is much more accurate than the one-sided version.

Write `num_deriv(f, x, h=1e-5)` using the central difference.

## Example

```text
num_deriv(lambda x: x**3, 2.0)    ->  12.0000000...     (the exact slope is 3 x^2 = 12)
num_deriv(math.sin, 0.0)          ->  1.0
```
