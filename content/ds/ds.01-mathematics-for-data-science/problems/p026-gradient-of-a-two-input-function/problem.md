# Gradient of a two-input function

Chapter section 7.1. For `f(x, y) = x^2 y + 3 y` the **gradient** is the vector of partial derivatives `[df/dx, df/dy]`: differentiate with respect to one variable while treating the other as a constant.

Write `grad_f(p)` for the point `p = [x, y]` and return the gradient as a NumPy array of two numbers.

## Example

```text
grad_f([1, 2])   ->  [4, 4]       (df/dx = 2xy = 4 and df/dy = x^2 + 3 = 4)
```
