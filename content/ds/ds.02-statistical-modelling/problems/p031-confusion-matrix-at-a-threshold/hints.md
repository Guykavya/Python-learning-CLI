## Hint 1

How do you turn `p` and the threshold into an array of predictions (0 or 1)? Then each cell is a count of rows with a particular pair (actual, predicted).

## Hint 2

```text
pred = (p >= threshold)
TP = count(y == 1 and pred)     FP = count(y == 0 and pred)
FN = count(y == 1 and not pred) TN = count(y == 0 and not pred)
```
