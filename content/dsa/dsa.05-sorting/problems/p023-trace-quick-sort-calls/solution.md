## Approach

Follow the code call by call. The partition puts the pivot in its final position; the two sides are sorted independently by the two recursive calls.

## Expected output

```text
depth 0 pivot 5 at 2 [3, 1, 5, 6, 8]
depth 1 pivot 1 at 0 [1, 3, 5, 6, 8]
depth 2 base 0 -1
depth 2 base 1 1
depth 1 pivot 8 at 4 [1, 3, 5, 6, 8]
depth 2 base 3 3
depth 2 base 5 4
[1, 3, 5, 6, 8]
```

## Why

Each pivot ends in its final place, so after `n` pivots (one per non-base call) the list is sorted. On sorted input the pivot is always the largest, one side is empty, and the depth becomes `n` (the O(n^2) worst case). A random or median-of-three pivot makes that very unlikely.
