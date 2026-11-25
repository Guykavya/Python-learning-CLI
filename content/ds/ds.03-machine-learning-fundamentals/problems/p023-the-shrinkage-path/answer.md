## Model answer

1. **Ridge**: every coefficient is shrunk **smoothly towards 0** as `alpha` grows (x0: 3.10, 3.09, 2.97, 2.11, 0.54). The junk coefficients (x3, x9) stay small but non-zero. **None reaches exactly 0**: the "exact zeros" column is 0 for every alpha.
2. **Lasso**: the coefficients also shrink, but the weak ones hit **exactly 0** and stay there. Already at `alpha = 0.1` five of the ten coefficients are exactly 0, including the junk `x3` and `x9`, while `x0, x1, x2` survive. At `alpha = 0.3` seven are zero (all junk removed, only the three real features remain, slightly shrunk). At `alpha = 10` everything is zero.
3. The ridge penalty is **squared** (`b^2`): near 0 it is flat and smooth, so its pull gets weaker as `b` gets small and the minimum never lands on exactly 0. The lasso penalty is the **absolute value** (`|b|`): it has a **corner** at 0 and a constant pull however small `b` is, so for a weak feature the penalty beats the small gain in fit and the coefficient sits at exactly 0.
4. Both penalties add up the size of the coefficients, and the size of a coefficient depends on the units of its feature. A feature measured in thousands has a tiny coefficient and is hardly penalised. Standardise first so the penalty treats features equally.
5. Use **lasso** to **select** features (sparse model). Use **ridge** to **stabilise** a model with correlated features: it shares the weight among them, whereas lasso tends to keep one and drop the others.

**Checklist: your answer should mention**
- [ ] ridge shrinks all coefficients smoothly and never to exactly zero
- [ ] lasso sets some coefficients to exactly zero (feature selection), e.g. the junk features at alpha 0.1
- [ ] squared penalty is smooth at 0, absolute-value penalty has a corner
- [ ] scale the features first, because the penalty depends on units
- [ ] lasso for selection, ridge for correlated features
