## Model answer

**Work.** `solve(A, b)` factorises `A` once (LU, about `2n^3/3` operations) and then does two cheap triangular solves. `inv(A)` is the same as solving `n` systems, one for every column of the identity, which costs about three times as much, and then you still have to multiply `inv(A) @ b`. You compute and throw away `n - 1` columns you did not need.

**Accuracy.** The inverse is rounded to doubles, and the product with `b` rounds again; the errors add up, especially when `A` is ill-conditioned. `solve` works on the factors directly and its residual `A x - b` is usually much smaller.

**Many right-hand sides.** If you need `x` for many different `b` with the same `A`, factorise once and reuse the factors (`scipy.linalg.lu_factor` / `lu_solve`): each extra `b` costs only `O(n^2)`. To time this fairly, repeat each call several times and take the **best** time with the chapter's `best_of`, because a single timing includes noise from the operating system.

**Checklist: your answer should mention**
- [ ] `inv` does about three times the work of `solve` (a whole matrix instead of one vector)
- [ ] the inverse and the product add rounding error: `solve` is more accurate
- [ ] factorise once and reuse for many `b`
- [ ] timing with `best_of` (best of several repeats)
