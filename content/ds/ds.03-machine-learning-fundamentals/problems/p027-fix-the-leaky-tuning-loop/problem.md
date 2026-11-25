# Fix the leaky tuning loop

Chapter section 10. A colleague tunes the penalty `alpha` of a ridge model and reports the result. The code **picks `alpha` by the score on the test set and then reports that same test score**. Open `solution.py` (it contains the colleague's code) and fix it.

What the function must do (`tune_and_report(X_train, y_train, X_test, y_test, alphas)`):

1. choose `alpha` from `alphas` using **only the training data**: the mean R-squared of `cross_val_score(Ridge(alpha=a), X_train, y_train, cv=5)` (plain 5-fold, default scoring); the first best alpha wins a tie
2. refit `Ridge(alpha=best)` on the **whole training set**
3. score it on the test set **once** (`score`, the R-squared)
4. return `(best_alpha, test_score)`

## Example

```text
tune_and_report(X_tr, y_tr, X_te, y_te, alphas)  ->  (316.2, 0.013)    # an honest, modest score
the colleague's version                           ->  (31.6, 0.155)     # optimistic: it picked the best of 13 test scores
```
