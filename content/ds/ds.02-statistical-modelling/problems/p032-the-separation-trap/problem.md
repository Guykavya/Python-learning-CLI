# The separation trap

Chapter section 13.10. If a predictor (or a combination) separates the 0s from the 1s perfectly, maximum likelihood has no finite answer: the coefficient grows without bound. statsmodels may print a warning and return a huge coefficient; older versions raised `PerfectSeparationError`. A report built on such a fit is nonsense.

Write `safe_logit(X, y)` where `X` already includes the constant column. It tries to fit `sm.Logit(y, X)` and returns a tuple `(result, reason)`:

- on a normal fit: `(result, "ok")`
- if the data are perfectly (or almost perfectly) separated: `(None, reason)` where `reason` is a string that contains the word `separation`
- if the design matrix is singular (its rank, `np.linalg.matrix_rank(X)`, is lower than its number of columns, or the fit raises `numpy.linalg.LinAlgError`): `(None, reason)` where `reason` contains `singular`. Check the rank **before** fitting: statsmodels quietly uses a pseudo-inverse for a rank-deficient matrix and returns an answer that means nothing.

Recognise separation by **any** of: an exception whose name or message mentions separation; a warning (from the fit) whose class name or message mentions separation; or an absurd coefficient (any `|coefficient| > 15`). Do not let warnings escape to the caller.

## Example

```text
x = [-3, -2, -1, -0.5, 0.5, 1, 2, 3]   y = [0, 0, 0, 0, 1, 1, 1, 1]      # x > 0 gives y = 1 exactly
safe_logit(X, y)   ->  (None, "perfect separation: ...")
```
