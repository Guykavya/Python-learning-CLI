## Hint 1

What are the numerator and the denominator? Which variance estimate (`ddof`) goes into the pooled formula, and how is each group weighted?

## Hint 2

```text
va, vb = a.var(ddof=1), b.var(ddof=1)
sp = sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
return (a.mean() - b.mean()) / sp
```
