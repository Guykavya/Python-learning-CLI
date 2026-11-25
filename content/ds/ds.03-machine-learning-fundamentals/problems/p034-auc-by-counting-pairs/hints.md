## Hint 1

Which pairs does `AUC = 0.75` count in the first example? Positives 0.35 and 0.8, negatives 0.1 and 0.4: how many of the 4 pairs does a positive win?

## Hint 2

```text
ranks = rankdata(score)                        # average ranks for ties
n_pos = sum(y == 1); n_neg = len(y) - n_pos
return (ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
```
