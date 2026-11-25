## Hint 1

Start from the mask `valid = ~np.isnan(x)`. How do you count the `True`s in each column? How do you get the sum of the valid values only, if `nan + anything` is `nan`?

## Hint 2

The warning comes from dividing by a count of 0. `np.divide(a, b, out=..., where=...)` (Ch. 10.6) divides only where the mask is true and leaves the other slots of `out` alone. What should `out` start as, so that those slots end up `nan`?

## Hint 3

```text
x = float array;  valid = ~isnan(x);  count = valid.sum(axis=0)
total = where(valid, x, 0).sum(axis=0)
mean  = divide(total, count, out=full(cols, nan), where=count > 0)
dev   = where(valid, x - mean, 0)
var   = divide((dev ** 2).sum(axis=0), count, out=full(cols, nan), where=count > 0)
return {"count": count, "mean": mean, "std": sqrt(var)}
```
