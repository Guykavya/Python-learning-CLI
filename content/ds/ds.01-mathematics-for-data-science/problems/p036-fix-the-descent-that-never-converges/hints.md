## Hint 1

Compare the sign of `loss_grad` with the formula `2/n X^T (X w - y)`. And compute the standard deviation of each column of the data.

## Hint 2

Fix 1: write the residual as `X @ w - y`. Fix 2: standardise each column with the **training** mean and std (use the same numbers for `X_new`), then add the intercept, then run the descent.
