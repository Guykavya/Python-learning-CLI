## Hint 1

Draw a number line with the edges 10, 20, 30, which make four bins: below 10, 10–20, 20–30, above 30. Only 10, 20 and 30 are hard; for every other value both settings agree. For the value 20: with `right=False`, which bin owns its left edge?

## Hint 2

```text
digitize(right=False): count of edges <= v      (v on an edge goes UP)
digitize(right=True):  count of edges <  v      (v on an edge stays DOWN)
searchsorted left:     count of edges <  v
searchsorted right:    count of edges <= v
labels[idx]:           pick label number idx
bincount(idx, minlength=4): how many values got 0, 1, 2, 3
```
