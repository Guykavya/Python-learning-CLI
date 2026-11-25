## Hint 1

Do it on paper for `(3, 4)` and `(3, 4, 1)`: write `(1, 3, 4)` under `(3, 4, 1)`. How do you build the padded tuple in Python? (`(1,) * k + tuple(s)`.) Then, for one axis, what does the set of lengths **other than 1** tell you?

## Hint 2

For one axis, collect `{n for n in lengths if n != 1}`. Empty set: the result is 1. One element: that is the result (even if it is 0). Two or more: error. Why does `max(lengths)` fail for `(0,)` and `(1,)`?

## Hint 3

```text
if no shapes: return ()
ndim = longest length;  padded = [(1,) * (ndim - len(s)) + tuple(s) for s in shapes]
result = [1] * ndim
for axis from ndim - 1 down to 0:
    not_one = set of padded[i][axis] that are != 1
    if len(not_one) > 1: raise ValueError(f"... axis {axis} ...")
    result[axis] = the one value, or 1
return tuple(result)
```
