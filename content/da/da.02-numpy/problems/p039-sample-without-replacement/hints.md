## Hint 1

Do not draw rows; draw **row positions**. Which Generator method picks `k` different numbers from `0 … n-1` (Ch. 13.3)? Which keyword forbids repeats?

## Hint 2

Once you have the positions `idx` (an integer array), how do you get those rows of `x` in that order (Ch. 9)? Is the result of fancy indexing a view or a copy?

## Hint 3

```text
x = asarray(x);  n = len(x)
if not 0 <= k <= n: raise ValueError(f"... k={k} ... n={n}")
idx = rng.choice(n, size=k, replace=False)
return x[idx]
```
