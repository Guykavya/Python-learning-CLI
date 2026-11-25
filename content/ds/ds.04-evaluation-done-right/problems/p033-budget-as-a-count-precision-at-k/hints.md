## Hint 1

Which rows are in the top 2 when two scores are equal? What does `kind='stable'` guarantee about the order of equal values?

## Hint 2

```text
order = argsort(-score, kind="stable")[:k]
precision = mean(y[order]); recall = sum(y[order]) / sum(y) (0.0 if no positives)
```
