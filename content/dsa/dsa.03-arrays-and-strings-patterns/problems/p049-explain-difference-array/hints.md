## Hint 1

Write the final added amounts for one update as a row: `0 5 5 5 0 0`. Now write the differences between
neighbours: position 0 minus nothing, position 1 minus position 0, and so on. Where are they nonzero?

## Hint 2

The running total at `i` is `d[0] + d[1] + ... + d[i]`. For `i` between `l` and `r` it includes the `+v` but not the
`-v`. For `i > r` it includes both. For `i < l` it includes neither.

## Hint 3

For many updates: the prefix sum of `d1 + d2` equals (prefix sum of `d1`) + (prefix sum of `d2`), because addition can be
reordered. So one pass at the end handles every update at once.

```
d[l] += v      # from l on, everything is v higher
d[r + 1] -= v  # from r + 1 on, take it back
prefix sum of d = the amount added to each position
```
