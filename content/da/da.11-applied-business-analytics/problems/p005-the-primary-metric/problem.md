# The primary metric

Chapter section 2.5. The primary metric of the banner test is **conversion**. Given `kA` conversions among `nA` visitors in A and `kB` among `nB` in B, write
`two_prop(kA, nA, kB, nB, level=0.95)` that returns a dict with the keys

| key | meaning |
|---|---|
| `A`, `B` | conversion rates `kA / nA`, `kB / nB` |
| `diff` | `B - A` (in proportions; negative if B is worse) |
| `lo`, `hi` | confidence interval of `diff`: `diff -/+ z * se` with the **unpooled** `se = sqrt(pA(1-pA)/nA + pB(1-pB)/nB)` and `z = norm.ppf(1 - (1 - level)/2)` |
| `rel_lift` | `diff / A` |
| `p` | two-sided p-value of the z-test with the **pooled** rate `pp = (kA + kB) / (nA + nB)`: `z = diff / sqrt(pp (1 - pp) (1/nA + 1/nB))`, `p = 2 (1 - Phi(|z|))` |

All values as plain floats.

## Example

`two_prop(720, 12000, 790, 12000)`: A 6.00%, B 6.58%, difference +0.58 points, 95% CI -0.03 to +1.20 points, p = 0.063. The interval includes 0: not significant at 5%.
