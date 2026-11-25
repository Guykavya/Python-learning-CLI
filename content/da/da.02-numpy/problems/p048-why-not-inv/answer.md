## Model answer

**Why `solve`: work.** `inv(A) @ b` does two jobs where one is enough. To get the inverse, NumPy factorises `A` (an LU decomposition) and then solves for every column of the identity matrix, building `n` columns you never asked for; then it multiplies by `b`. `solve(A, b)` makes the same factorisation and uses it once, for `b` only. So it is **slower** to go through `inv`, roughly two to three times the work for one right-hand side, and it needs memory for the whole inverse.

**Why `solve`: accuracy.** Every extra step adds rounding error, and the explicit inverse of a nearly **singular** matrix is itself computed inaccurately. In the Hilbert test the error was `1.69e-04` with `solve` and `5.55e-03` with `inv`: about 30 times **less accurate**. So **solve directly**.

**The condition number.** It measures how much a small relative change in the input (`b` or `A`) can be amplified in the answer. Fact 2 shows it: the two rows of `A` are almost the same equation, so the solution is poorly determined, and a change of 0.0001 in `b` moved `x` from `[1, 1]` to `[0, 2]`. Its condition number is `4e+04`: small input errors can grow about 40,000 times. A singular matrix has an infinite condition number (no unique solution at all).

**Digits.** `float64` carries about 16 significant digits; a condition number of `10^k` can cost about `k` of them. With `10^13` only about 3 digits can be trusted, which is what the Hilbert errors (around `10^-4` on values of 1) show.

**The residual.** `A @ x - b` (or `np.allclose(A @ x, b)`) checks that `x` really satisfies the equations, and catches bugs such as a transposed matrix. But for an ill-conditioned matrix a tiny residual does **not** mean `x` is close to the true solution: many very different `x` fit almost equally well. So check the residual **and** look at `np.linalg.cond(A)`.

**When the inverse is justified.** When you need the inverse matrix itself as a result, for example the diagonal of `inv(X.T @ X)` for the standard errors of regression coefficients (ds.02). Even then, solving with a factorisation is often preferred.

**Checklist: your answer should mention**
- [ ] `inv` then `@` is **slower** (extra work, the whole inverse) than **solving directly**
- [ ] `inv` is **less accurate** (the Hilbert errors: 1.69e-04 vs 5.55e-03)
- [ ] the **condition number** = amplification of input errors; large for nearly **singular** matrices
- [ ] about 16 digits in float64 minus about 13 lost for cond ≈ 10^13
- [ ] **check the residual**, but a small residual does not prove accuracy when the condition number is large
- [ ] compute an inverse only when the inverse itself is needed
