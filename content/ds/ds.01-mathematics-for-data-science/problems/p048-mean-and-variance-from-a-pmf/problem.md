# Mean and variance from a pmf

Chapter section 11.1. For a discrete random variable with values `x_i` and probabilities `p_i`, the **mean** is `sum(x_i p_i)` and the **variance** is `sum((x_i - mean)^2 p_i)`.

Write `mean_var(values, probs)` returning `(mean, variance)`. Raise `ValueError` if the probabilities do not add up to 1 (within `1e-9`), if any is negative, or if the two lists have different lengths.

## Example

```text
a fair die: mean_var([1, 2, 3, 4, 5, 6], [1/6] * 6)  ->  (3.5, 2.9167)     # 35/12
```
