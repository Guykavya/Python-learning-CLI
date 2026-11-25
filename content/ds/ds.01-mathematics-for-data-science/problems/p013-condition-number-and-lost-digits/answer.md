## Model answer

**Condition number.** The condition number `kappa(A)` is the ratio of the largest to the smallest singular value. It is the factor by which a small **relative** error in `b` (or in the entries of `A`) can grow in the relative error of the solution `x`. `make_near_singular(1e-10)` has `kappa` of about `4e10`: the two rows are almost parallel, so the smallest singular value is about `eps / 2`.

**Digits lost.** A double carries about 16 significant digits. You lose about `log10(kappa)` of them, here about 10 to 11, so only 5 or 6 digits of `x` are trustworthy. The solver is not buggy: even the best algorithm cannot recover information the matrix has already blurred. That is a property of the **problem**, not of the method.

**Normal equations.** The singular values of `A^T A` are the squares of those of `A`, so `kappa(A^T A) = kappa(A)^2`. With `kappa = 4e10` the normal equations have `kappa` near `1.6e21`, which is beyond what doubles can represent: all digits are lost. Forming `A^T A` turns a hard problem into an impossible one. Use `np.linalg.lstsq` (SVD) or a QR factorisation, which work on `A` itself.

**Checklist: your answer should mention**
- [ ] condition number = largest / smallest singular value (amplification of relative error)
- [ ] digits lost ~ log10(kappa), starting from about 16
- [ ] `A^T A` squares kappa
- [ ] use `lstsq`/QR/SVD instead of the normal equations for ill-conditioned problems
