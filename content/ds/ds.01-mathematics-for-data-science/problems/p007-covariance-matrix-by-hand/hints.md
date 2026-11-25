## Hint 1

Subtract the column means first. Which matrix product gives all the pairwise sums of products at once? What do you divide by?

## Hint 2

```text
Xc = X - X.mean(axis=0)
return Xc.T @ Xc / (n - 1)
```
