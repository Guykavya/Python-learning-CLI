## Hint 1

Which denominators can be zero? Write one small helper that divides and returns 0.0 when the denominator is 0, and use it for every ratio.

## Hint 2

```text
def ratio(a, b): return a / b if b else 0.0
precision = ratio(TP, TP + FP); recall = ratio(TP, TP + FN)
f1 = ratio(2 * precision * recall, precision + recall)
```
