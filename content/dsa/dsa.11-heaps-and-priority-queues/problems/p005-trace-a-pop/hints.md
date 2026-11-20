## Hint 1

The heap is `[1, 2, 6, 3, 4, 7, 8]`. The first pop removes `1`. `a.pop()` takes the **last** item, `8`, so the list has 6 items `[1, 2, 6, 3, 4, 7]`; then `a[0] = 8` overwrites the old root: `[8, 2, 6, 3, 4, 7]`. That is the first list line. Now `8` sits at index 0 with the children `2` (index 1) and `6` (index 2).

## Hint 2

Which child is smaller, `2` or `6`? That one swaps with `8`. The `8` is then at index 1 with the children at indexes 3 and 4 (`3` and `4`). The smaller child is `3`: swap again. Now `8` is at index 3, and its children would be at indexes 7 and 8, but the list has only 6 items: that is the `stop` line. The first pop returns `1`; the heap is `[2, 3, 6, 8, 4, 7]`.

Do the second pop in the same way. The item moved to the root is the last one, `7`; the children of the root are `3` and `6`.
