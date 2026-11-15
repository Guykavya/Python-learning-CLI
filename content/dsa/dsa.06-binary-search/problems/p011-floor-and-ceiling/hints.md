## Hint 1

The ceiling is the first element `>= x`. The floor is the last element `<= x`. Which of the two bounds from this chapter gives each index?

## Hint 2

`lower_bound(x)` is the index of the ceiling (valid if `< n`). `upper_bound(x) - 1` is the index of the floor (valid if `>= 0`).

## Hint 3

```
i = first index with a[i] >= x        # ceiling at i if i < n
j = first index with a[j] > x         # floor at j - 1 if j > 0
print(a[j-1] if j > 0 else "none", a[i] if i < n else "none")
```
