## Approach

Evaluate the function on both sides of `x` and divide the difference by the distance between the points.

## Code

```python
def num_deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
```

## Complexity

Two calls of `f`.

## Another way

A five-point stencil is even more accurate, but the central difference is the standard choice.
