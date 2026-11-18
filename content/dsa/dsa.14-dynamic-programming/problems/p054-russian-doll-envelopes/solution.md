## Approach

Reduce a 2-D problem to the 1-D LIS (chapter section 13, "Variations that reuse LIS").

1. Sort the envelopes by width. A chain is now a subsequence of this list in which both width and height strictly increase.
2. Envelopes with **equal width** cannot both be in a chain. Sort them by height **descending**. Then their heights go down, so a strictly increasing subsequence of heights takes at most one of them. After this, "heights strictly increase" already implies "widths strictly increase".
3. The answer is the strictly increasing LIS of the heights, with `bisect_left` (p052).

```python
from bisect import bisect_left


def max_envelopes(envelopes):
    order = sorted(envelopes, key=lambda e: (e[0], -e[1]))   # width up, height DOWN on ties
    tails = []
    for _, h in order:
        k = bisect_left(tails, h)            # strictly increasing heights
        if k == len(tails):
            tails.append(h)
        else:
            tails[k] = h
    return len(tails)
```

Why does step 2 work? Take any increasing subsequence of heights in the sorted order. Two neighbours in it have different widths (equal widths come with non-increasing heights), and the later one has the larger width (the list is sorted by width). So it is a valid chain. Conversely, every chain sorted by width is such a subsequence.

Example `[(4, 5), (4, 6), (6, 7), (2, 3), (1, 1)]`: sorted with the key it is `(1,1), (2,3), (4,6), (4,5), (6,7)`, heights `1, 3, 6, 5, 7`, LIS 4 (`1, 3, 5, 7`). With heights sorted **ascending** on ties you get `1, 3, 5, 6, 7` and the wrong answer 5.

## Complexity

`O(n log n)` for the sort and the LIS, `O(n)` space.

## Another way

Sort by `(width, height)` and use the `O(n^2)` DP `f[i] = 1 + max f[j]` over `j < i` with `w[j] < w[i]` **and** `h[j] < h[i]`. With the double strict check the tie order does not matter. It is correct and a good oracle (the tests use it), but too slow for 100,000 envelopes.
