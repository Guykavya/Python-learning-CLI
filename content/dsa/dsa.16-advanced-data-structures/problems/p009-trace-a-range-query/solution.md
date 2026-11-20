## Approach

Follow the three cases of chapter section 3 node by node, depth first, left child before right child. An inside node is taken whole and not entered; an outside node is skipped; a partial node is printed and split.

## Expected output

```text
1 [0,8) partial
  2 [0,4) partial
    4 [0,2) outside
    5 [2,4) inside 10
  3 [4,8) partial
    6 [4,6) inside 11
    7 [6,8) outside
sum: 21
1 [0,8) partial
  2 [0,4) partial
    4 [0,2) partial
      8 [0,1) outside
      9 [1,2) inside 1
    5 [2,4) inside 10
  3 [4,8) partial
    6 [4,6) inside 11
    7 [6,8) partial
      14 [6,7) inside 6
      15 [7,8) outside
sum: 28
```

## Why

- `query(2, 6)`: the range `[2, 6)` is exactly `[2,4)` + `[4,6)`, two whole nodes: `10 + 11 = 21`. Only the root and nodes 2 and 3 are partial.
- `query(1, 7)`: the edges 1 and 7 fall inside `[0,2)` and `[6,8)`, so those split down to leaves: leaf 9 (`a[1] = 1`) and leaf 14 (`a[6] = 6`) are taken; nodes 5 and 6 are taken whole. `1 + 10 + 11 + 6 = 28`.

**After you answer.**

1. `query(2, 6)`: nodes 5 and 6, `[2,4) + [4,6) = [2,6)`. `query(1, 7)`: nodes 9, 5, 6, 14, `[1,2) + [2,4) + [4,6) + [6,7) = [1,7)`.
2. Half-open ranges: `[4,6)` is the positions 4 and 5, all inside `[2,6)`. `[6,8)` is the positions 6 and 7; the query `[2,6)` ends **before** 6 (`r = 6 <= lo = 6`), so they share nothing.
3. 7 visits for a range of 4 elements and 11 visits for 6: the count grows with the number of levels (at most about 4 per level), not with the length of the range.

## Another way

Count without printing: the inside nodes form the canonical cover of the range, which you can find bottom-up as the iterative tree does (p006): for `[1, 7)` it takes leaf 9 and leaf 14 at the bottom level, then nodes 5 and 6 one level up.
