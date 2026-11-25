# The gradient check

Chapter section 7.3. Gradients written by hand are easy to get wrong. A **gradient check** compares your gradient with a numerical one and reports the **relative error**:

`|g_analytic - g_numeric| / max(|g_analytic| + |g_numeric|, 1e-12)` (norms of vectors).

Write `grad_check(f, grad, p, h=1e-5)`: `f` takes a NumPy vector and returns a number, `grad` returns the analytic gradient, `p` is the point. Build the numerical gradient with central differences, one coordinate at a time, and return the relative error as a float. If both gradients are 0 return 0.

## Example

```text
f(p) = p . p      grad(p) = 2 p       at p = [1, 2]  ->  about 1e-11   (correct)
the same with grad(p) = -2 p          ->  2.0        (sign error: totally wrong)
```
