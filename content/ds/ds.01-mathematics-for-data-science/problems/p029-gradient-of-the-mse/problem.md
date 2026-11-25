# Gradient of the MSE

Chapter section 7.4. For a linear model `y_hat = X w` the **mean squared error** is `L(w) = (1/n) |X w - y|^2`. Its gradient with respect to the weights is `(2/n) X^T (X w - y)`.

Write `mse_grad(w, X, y)` returning that gradient as an array of the same shape as `w`. `X` has `n` rows and `d` columns.

## Example

```text
X = [[1], [2]]   y = [1, 2]   w = [0]
mse_grad([0], X, y) = 2/2 * (1*(0-1) + 2*(0-2)) = -5
```
