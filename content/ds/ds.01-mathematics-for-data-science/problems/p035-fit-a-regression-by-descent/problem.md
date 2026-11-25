# Fit a regression by descent

Chapter section 8.3. Linear regression can be fitted by gradient descent on the mean squared error. The features are already standardised.

Write `fit_linear_gd(X, y, lr, steps)` that adds an **intercept column of ones** as the first column, starts from zero weights, runs `steps` steps with the gradient `(2/n) A^T (A w - y)` and returns the weight vector `[intercept, w1, ..., wd]`.

## Example

```text
X = [[-1], [0], [1]]   y = [1, 3, 5]      (the line y = 3 + 2 x)
fit_linear_gd(X, y, 0.1, 500)  ->  [3, 2]   (about)
```
