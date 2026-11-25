# Fix the descent that never converges

Chapter section 8.4. The code in `starter.py` fits a linear model by gradient descent and predicts for new rows, but it **blows up** (the weights become `inf` or `nan`). There are **two bugs**. Find both and fix them:

1. the gradient in `loss_grad` is wrong (it passes no gradient check);
2. `fit_and_predict` runs on **raw features** that live on very different scales (a column of about 1 and a column of about 1,000), so any usable learning rate is too big for one and too small for the other.

Keep the two function names and signatures. `fit_and_predict(X, y, X_new, lr=0.1, steps=500)` must return the predictions for `X_new`. Keep the gradient in `loss_grad(w, X, y)`, for the mean squared error `mean((X w - y)^2)`, as the test checks it separately.

## Example

```text
X = columns [1, 1000] ...    fit_and_predict(X, y, X_new)  ->  finite predictions close to the least-squares ones
```

## How to find it

Run the gradient check of problem 27 on `loss_grad` first. Then look at the size of `X.T @ X`.
