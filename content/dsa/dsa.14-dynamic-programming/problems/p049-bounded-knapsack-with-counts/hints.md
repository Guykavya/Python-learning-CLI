## Hint 1

The easy correct idea: write each copy as its own item and run the 0/1 knapsack (downward loop). For `(2, 3, 2)` that is two items `(2, 3)` and `(2, 3)`. It is right, but with 1000 copies of 100 kinds you have 100,000 items. Where is the waste? Many different choices ("copy 1 and copy 3" vs "copy 2 and copy 4") mean the same thing.

## Hint 2

**Binary splitting.** Split `count` copies into bundles of size `1, 2, 4, 8, ...` while they fit, and one last bundle with whatever is left. For `count = 13`: `1, 2, 4, 6`. Any number from 0 to 13 is a sum of some of these bundles, each used at most once (try 5 = 1 + 4, 11 = 1 + 4 + 6, 13 = all). And no choice of bundles exceeds 13. A bundle of `b` copies is one 0/1 item with weight `b * weight` and value `b * value`. About `log2(count)` bundles instead of `count` copies.

## Hint 3

```
g = [0] * (W + 1)
for weight, value, count in items:
    b = 1
    while count > 0:
        take = min(b, count)
        bw, bv = take * weight, take * value
        for w from W down to bw:              # a bundle is a 0/1 item
            g[w] = max(g[w], g[w - bw] + bv)
        count -= take
        b *= 2
return g[W]
```
