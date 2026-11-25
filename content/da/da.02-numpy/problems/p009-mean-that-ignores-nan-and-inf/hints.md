## Hint 1

Which NumPy function is `False` for `nan`, `inf` and `-inf` at once? How do you count the `False` places of a mask, and what should happen *before* you call `mean` if the mask has no `True` at all?

## Hint 2

```text
ok = np.isfinite(x)
n_dropped = x.size - count of True in ok
if no True in ok:
    return nan, n_dropped          # do not call mean on nothing
return float(x[ok].mean()), n_dropped
```
