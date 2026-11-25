# Gradient of the log-loss

Chapter section 7.5. For classification with labels `y` in `{0, 1}` and scores `z = X w`, the mean **log-loss** is `L(w) = mean(log(1 + exp(z)) - y z)`. Through the chain rule its gradient is `X^T (sigmoid(z) - y) / n`.

Write `logloss_grad(w, X, y)`. The catch is **stability**: `exp(z)` overflows for large `z`. Compute the sigmoid so that it never evaluates `exp` of a large positive number: for `z >= 0` use `1 / (1 + exp(-z))`, for `z < 0` use `exp(z) / (1 + exp(z))`. The test runs your code with `np.errstate(over="raise")`, so any overflow is an error.

## Example

```text
w = [0]   X = [[1], [-1]]   y = [1, 0]     sigmoid(0) = 0.5
logloss_grad = X^T (0.5 - y) / 2 = (1 * (-0.5) + (-1) * 0.5) / 2 = -0.5
```
