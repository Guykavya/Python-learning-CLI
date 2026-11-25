## Hint 1

Write Pearson first, from the formula: centre both variables, multiply, add. What do you divide by, and when is that zero? For Spearman, which transformation do you apply before reusing Pearson?

## Hint 2

```text
dx = x - x.mean(); dy = y - y.mean()
denom = sqrt((dx ** 2).sum() * (dy ** 2).sum()) ; if denom == 0: raise ValueError
pearson = (dx * dy).sum() / denom ; spearman = pearson(rankdata(x), rankdata(y))
```
