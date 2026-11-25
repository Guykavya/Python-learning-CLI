## Walk-through

| b | shortcut | exp(b) | exact |
|---|---|---|---|
| 0.02 | +2.00 | 1.0202 | +2.02 |
| 0.10 | +10.00 | 1.10517 | +10.52 |
| 0.40 | +40.00 | 1.49182 | +49.18 |
| -0.40 | -40.00 | 0.67032 | -32.97 |

A negative coefficient never gives a drop bigger than 100 percent: `exp(b)` stays positive. A drop of 40 percent corresponds to `log(0.6) = -0.51`, not -0.40.

## Another way

`np.expm1(b)` computes `exp(b) - 1` accurately for tiny `b`.
