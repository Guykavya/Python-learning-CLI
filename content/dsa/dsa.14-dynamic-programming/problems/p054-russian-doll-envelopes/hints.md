## Hint 1

Sort by width. Then a nesting chain is a subsequence of the sorted list whose widths **and** heights strictly increase. If no two widths were equal, "widths increase" would be automatic and only the heights would matter: the answer would be the strictly increasing LIS of the heights, in `O(n log n)` with `bisect_left` (p052).

## Hint 2

The trouble is equal widths: two envelopes of width 3 must never be in the same chain. Sort the envelopes of equal width by height **descending**. Then, inside one width, the heights go down, and a strictly increasing subsequence of heights can take **at most one** of them. Sort key: `(width, -height)`.

## Hint 3

```
envelopes sorted by key (w, -h)
heights = [h for w, h in that order]
return LIS length of heights, strictly increasing, with bisect_left
```
