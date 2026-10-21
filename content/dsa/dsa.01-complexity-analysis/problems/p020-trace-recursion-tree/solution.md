## Walkthrough

For `n = 8`:

| level | pieces | work on this level |
|---|---|---|
| 0 | 8 | 8 |
| 1 | 4, 4 | 8 |
| 2 | 2, 2, 2, 2 | 8 |
| 3 | 1 x 8 | 8 |

Calls: `1 + 2 + 4 + 8 = 15`. Work: 4 levels of 8 = 32.

For `n = 10`: the tree is `10` -> `5, 5`; each `5` -> `2, 3`; each `2` -> `1, 1`; each `3` -> `1, 2`, and that
`2` -> `1, 1`.

- `calls(1) = 1`, `calls(2) = 3`, `calls(3) = 1 + 1 + 3 = 5`, `calls(5) = 1 + 3 + 5 = 9`, `calls(10) = 1 + 9 + 9 = 19`.
- `work(1) = 1`, `work(2) = 2 + 1 + 1 = 4`, `work(3) = 3 + 1 + 4 = 8`, `work(5) = 5 + 4 + 8 = 17`,
  `work(10) = 10 + 17 + 17 = 44`.

Output:

```
1 1 1
2 3 4
4 7 12
8 15 32
16 31 80
10 19 44
```

## Key idea

For `n` a power of two, `calls = 2n - 1` (every piece of size 1 is a leaf, and a tree with `n` leaves where each
inner box has two children has `n - 1` inner boxes) and `work = n * (log2(n) + 1)`: each level adds up to `n`, and
there are `log2(n) + 1` levels.

This is the recurrence `T(n) = 2T(n/2) + n`, whose solution is O(n log n). It is why merge sort is O(n log n): the
halving gives `log n` levels, and each level does O(n) work in total.
