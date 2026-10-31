## Walkthrough

**Pushes** (append, then bubble up):

| push | after append | swaps | heap |
|---|---|---|---|
| 5 | `[5]` | none | `[5]` |
| 3 | `[5, 3]` | 3 < 5 | `[3, 5]` |
| 8 | `[3, 5, 8]` | none | `[3, 5, 8]` |
| 1 | `[3, 5, 8, 1]` | with 5 (index 1), then with 3 | `[1, 3, 8, 5]` |
| 9 | `[1, 3, 8, 5, 9]` | parent 3 is smaller | `[1, 3, 8, 5, 9]` |
| 2 | `[1, 3, 8, 5, 9, 2]` | with 8 (index 2); parent 1 is smaller | `[1, 3, 2, 5, 9, 8]` |

**heappop**: returns 1. The last item, 8, moves to the top: `[8, 3, 2, 5, 9]`. Its children
are 3 and 2; the smaller is 2, so swap: `[2, 3, 8, 5, 9]`. Index 2 has no children. Prints
`1 [2, 3, 8, 5, 9]`.

**heappushpop(h, 4)**: 4 is bigger than the root 2, so return 2 and put 4 on top:
`[4, 3, 8, 5, 9]`. Smaller child 3: swap, `[3, 4, 8, 5, 9]`. Now 4's children are 5 and 9, both
bigger: stop. Prints `2 [3, 4, 8, 5, 9]`.

**heappushpop(h, 0)**: 0 `<=` root 3, so 0 is returned at once and the heap is untouched.

**heapreplace(h, 0)**: always pops first. Returns 3, puts 0 on top: `[0, 4, 8, 5, 9]`; 0 is
smaller than its children, so no swaps. Prints `3 [0, 4, 8, 5, 9]`. Compare with the line above:
same item, different result.

**heapify([7, 6, 5, 4, 3, 2, 1])**: `7 // 2 - 1 = 2`, so sift indexes 2, 1, 0.
- index 2 (5): children 2 and 1 → swap with 1: `[7, 6, 1, 4, 3, 2, 5]`.
- index 1 (6): children 4 and 3 → swap with 3: `[7, 3, 1, 4, 6, 2, 5]`.
- index 0 (7): children 3 and 1 → swap with 1: `[1, 3, 7, 4, 6, 2, 5]`; now at index 2, children 2 and 5 → swap with 2: `[1, 3, 2, 4, 6, 7, 5]`.

**Three pops**:
- pop 1: 5 goes on top, `[5, 3, 2, 4, 6, 7]` → swap with 2 → `[2, 3, 5, 4, 6, 7]`; index 2's child is 7, stop.
- pop 2: 7 on top, `[7, 3, 5, 4, 6]` → swap with 3 → `[3, 7, 5, 4, 6]` → children 4, 6 → swap with 4 → `[3, 4, 5, 7, 6]`.
- pop 3: 6 on top, `[6, 4, 5, 7]` → swap with 4 → `[4, 6, 5, 7]`; child 7 is bigger, stop.

Prints `[1, 2, 3] [4, 6, 5, 7]`.

**Max-heap by negation**: push -2 → `[-2]`; push -7 → swaps → `[-7, -2]`; push -4 → parent -7 is
smaller → `[-7, -2, -4]`. `-m[0]` is 7, the largest original value.

## The exact output

```text
[5]
[3, 5]
[3, 5, 8]
[1, 3, 8, 5]
[1, 3, 8, 5, 9]
[1, 3, 2, 5, 9, 8]
1 [2, 3, 8, 5, 9]
2 [3, 4, 8, 5, 9]
0 [3, 4, 8, 5, 9]
3 [0, 4, 8, 5, 9]
[1, 3, 2, 4, 6, 7, 5]
[1, 2, 3] [4, 6, 5, 7]
[-7, -2, -4] 7
```

(CPython's C code moves items in a slightly different order inside a sift, but it always ends
with the same list as these textbook rules.)
