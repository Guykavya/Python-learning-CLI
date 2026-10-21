## Hint 1

`d.keys()` and `d.values()` give the names and the scores in the same order.

## Hint 2

`sum(d.values())` adds the scores. The values are ints, so join them with `str(v)` first.

## Hint 3

`max(d, key=d.get)` returns the key whose value is largest, and the first one among equals.
