## Model answer

**The wrong one is B.** `d/dw1 exp(w1^2)` needs the **chain rule**: the derivative of the outer function `exp(u)` is `exp(u)`, but it must be multiplied by the derivative of the inner function `u = w1^2`, which is `2 w1`. The claimed gradient forgot that factor: it should be `[2 w1 exp(w1^2), 1]`. A and C are correct (A has the factor 2 from the square and the factor 2 / -1 from the inner `2 w1 - w2`; C is the product rule on `w1 w2` inside `sin`).

**How the gradient check finds it.** The check builds a numerical gradient from the function alone: `(f(w + h e_i) - f(w - h e_i)) / (2 h)` for each coordinate, with `h` about `1e-5`. It then computes the relative error `|g_claimed - g_numeric| / (|g_claimed| + |g_numeric|)`. It does not trust any formula, so it disagrees exactly where the formula is wrong. At `w = [1, 0.5]` the measured relative errors are about `2e-12` for A, `0.32` for B and `9e-12` for C: tiny (rounding level) for the correct formulas and large for B. A correct gradient gives an error below about `1e-6`; a wrong one typically gives `1e-2` or more.

**Fix.** Replace the first component of B by `2 w1 exp(w1^2)` and run the check again, at several random points.

**Checklist: your answer should mention**
- [ ] B is wrong
- [ ] the missing factor `2 w1`, the derivative of the inner function
- [ ] the chain rule
- [ ] numerical gradient with central differences and a relative error
- [ ] small error (about 1e-6 or less) means correct, large error means wrong
