## Walkthrough: first call

Sorted: `-4 -1 -1 0 1 2` (indices 0 to 5), `n = 6`, so `i` runs from 0 to 3.

| i | l | r | sum | move |
|---|---|---|---|---|
| 0 | 1 | 5 | -4 - 1 + 2 = -3 | l+1 |
| 0 | 2 | 5 | -3 | l+1 |
| 0 | 3 | 5 | -4 + 0 + 2 = -2 | l+1 |
| 0 | 4 | 5 | -4 + 1 + 2 = -1 | l+1, now `l = r`, stop |
| 1 | 2 | 5 | -1 - 1 + 2 = 0 | found; `l = 3`, `r = 4`; `a[3] = 0 != a[2]`, `a[4] = 1 != a[5]`: no skips |
| 1 | 3 | 4 | -1 + 0 + 1 = 0 | found; `l = 4`, `r = 3`: stop |
| 2 | | | | `a[2] == a[1]`: `skip i 2` |
| 3 | 4 | 5 | 0 + 1 + 2 = 3 | r-1, stop |

## Second call

`0 0 0 0`: `i = 0`, `l = 1`, `r = 3`, sum 0, found. Then `l = 2`, `r = 2`, so both skip loops fail the `l < r` test
at once and print nothing. `i = 1` is a repeated value: `skip i 1`. `range(2)` stops there.

## Third call

Sorted: `-4 1 1 2 3 3`. `i = 0`, `l = 1`, `r = 5`: `-4 + 1 + 3 = 0`, found. Now `l = 2`, `r = 4`.
`a[2] = 1 == a[1]`: `skip l 2`, `l = 3`. `a[3] = 2 != a[2]`: stop. `a[4] = 3 == a[5]`: `skip r 4`, `r = 3`. Now
`l = r`: the skip loop and the main loop both stop.
`i = 1` (value 1): sums `1 + 1 + 3 = 5`, `5`, `1 + 1 + 2 = 4`, each `r-1`, until `r = l = 2`.
`i = 2`: same value as `a[1]`, `skip i 2`. `i = 3`: `2 + 3 + 3 = 8`, `r-1`, stop.

## Output

```
sorted -4 -1 -1 0 1 2
0 1 5 -3 l+1
0 2 5 -3 l+1
0 3 5 -2 l+1
0 4 5 -1 l+1
1 2 5 0 found
1 3 4 0 found
skip i 2
3 4 5 3 r-1
[(-1, -1, 2), (-1, 0, 1)]
sorted 0 0 0 0
0 1 3 0 found
skip i 1
[(0, 0, 0)]
sorted -4 1 1 2 3 3
0 1 5 0 found
skip l 2
skip r 4
1 2 5 5 r-1
1 2 4 5 r-1
1 2 3 4 r-1
skip i 2
3 4 5 8 r-1
[(-4, 1, 3)]
```

## Key ideas

- Sorting lets the inner loop be the pair-sum two-pointer search: a small sum means "move `l` right", a big sum
  "move `r` left". It also puts equal values next to each other, which is the only reason "compare with the
  neighbour" is enough to skip duplicates.
- The three skips remove repeated triplets: `skip i` stops the same first value from starting a second search;
  `skip l` and `skip r` stop the same second and third values after a hit.
- Total cost: O(n log n) to sort, plus O(n) for each `i`, so O(n^2). The skips do not change the order of growth;
  they only keep the output free of repeats.
