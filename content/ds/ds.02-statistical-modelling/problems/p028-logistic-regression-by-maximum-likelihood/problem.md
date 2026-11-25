# Logistic regression by maximum likelihood

Chapter section 13.3. Logistic regression has no closed form. The coefficients `b` maximise the log-likelihood

```text
loglik(b) = sum( y * log(p) + (1 - y) * log(1 - p) ),   p = 1 / (1 + exp(-X b))
```

A standard way to find the maximum is **Newton's method** (also called IRLS): start at `b = 0` and repeat

```text
p = sigmoid(X @ b)
gradient = X.T @ (y - p)
W = p * (1 - p)                       # one weight per row
hessian = X.T @ (X * W[:, None])      # = X' diag(W) X
b = b + solve(hessian, gradient)
```

until the change in `b` is smaller than `1e-10` (or after 50 steps).

Write `fit_logit(X, y)` where `X` is a NumPy array that **already contains a column of ones** and `y` is an array of 0/1. Return the coefficient vector as a 1-D array. Use NumPy only (no statsmodels or SciPy optimisers).

## Example

```text
X = column of ones + one feature; y = 0/1
fit_logit(X, y)   ->  array([-0.51, 0.97])     # same as sm.Logit(y, X).fit().params
```
