## Approach

Preorder walk: print the node, check the length, then visit children `x = start .. n` from left to right. A child's `start` is always one more than the value it just added.

## Expected output

```text
start 1 path []
start 2 path [1]
start 3 path [1, 2]
start 4 path [1, 3]
start 5 path [1, 4]
start 3 path [2]
start 4 path [2, 3]
start 5 path [2, 4]
start 4 path [3]
start 5 path [3, 4]
start 5 path [4]
[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
```

## Why

```text
go(1) []
├── go(2) [1] ── go(3) [1, 2] | go(4) [1, 3] | go(5) [1, 4]
├── go(3) [2] ── go(4) [2, 3] | go(5) [2, 4]
├── go(4) [3] ── go(5) [3, 4]
└── go(5) [4]          (empty loop: a dead end)
```

11 calls, 6 answers (4 choose 2 = 6). The call `go(5)` with path `[4]` is a doomed branch: one more number above 4 is needed, but none is left. The pruned loop for the root stops at `n - need + 1 = 4 - 2 + 1 = 3`, so the line `start 5 path [4]` disappears.
