## Hint 1

When `x` arrives, the inversions it closes are the earlier elements **strictly greater** than `x`. If a Fenwick tree counts how many earlier elements have each value, that is `seen - (earlier elements <= x)`, where `seen` is the number of earlier elements.

## Hint 2

Replace every value by its **rank** among the distinct values: `ranks = {v: i for i, v in enumerate(sorted(set(a)))}`. Equal values get equal ranks. Then "earlier elements `<= x`" is `prefix(rank + 1)`.

## Hint 3

```
bit = Fenwick(number of distinct values); inv = 0
for seen, x in enumerate(a):
    k = ranks[x]
    inv += seen - bit.prefix(k + 1)
    bit.add(k, 1)
```
