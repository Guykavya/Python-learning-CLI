## Hint 1

For one class `c`: what are TP, FP and FN? What is F1 in terms of those three counts? What does 'pooled' mean for micro?

## Hint 2

```text
for each class c: TP = count(y == c and p == c); FP = count(y != c and p == c); FN = count(y == c and p != c)
f1_c = 2 TP / (2 TP + FP + FN)  (0.0 when the denominator is 0)
macro = mean(f1_c); weighted = sum(f1_c * support_c) / n
micro = 2 sumTP / (2 sumTP + sumFP + sumFN)
```
