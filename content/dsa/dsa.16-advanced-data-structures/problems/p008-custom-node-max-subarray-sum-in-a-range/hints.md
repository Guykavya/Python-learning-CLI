## Hint 1

A crossing piece is a suffix of the left part glued to a prefix of the right part. So each node needs its best prefix and best suffix. To compute the joined range's best prefix you also need the left part's total.

## Hint 2

```
merge(x, y):
    total  = x.total + y.total
    prefix = max(x.prefix, x.total + y.prefix)
    suffix = max(y.suffix, y.total + x.suffix)
    best   = max(x.best, y.best, x.suffix + y.prefix)
```

A leaf `v` is `(v, v, v, v)`. The identity is `(0, -inf, -inf, -inf)`.

## Hint 3

Use the iterative tree of p006 (or a recursive one) with these records as values. In the iterative query keep a left and a right accumulator, because `merge(x, y) != merge(y, x)`.
