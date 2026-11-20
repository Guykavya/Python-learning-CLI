## Hint 1

Let `g[w]` be the best value with capacity `w`. Think about one item in the bag, any one, say item `i`. Remove it: what is left is a bag of capacity `w - wt[i]` filled **with any items, item `i` included**. So `g[w] = max(g[w - wt[i]] + val[i])` over the items that fit, and `g[w] = 0` when nothing fits.

## Hint 2

`g[w]` reads smaller capacities, which must already be final. Fill `w` from small to large. Either loop order works for a maximum (chapter section 11), as long as the capacity loop goes **upwards**.

## Hint 3

```
g = [0] * (W + 1)
for i in each item:
    for w from wt[i] up to W:
        g[w] = max(g[w], g[w - wt[i]] + val[i])
return g[W]
```

Compare with p036: the only change is the direction of the `w` loop.
