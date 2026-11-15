## Approach

Walk the recursion tree in preorder: print the node, then visit its children from left to right. The children of a node with `start = s` add `nums[s]`, `nums[s+1]`, ... and get `start` = the chosen position + 1.

## Expected output

```text
0 []
1 [1]
2 [1, 2]
3 [1, 2, 3]
3 [1, 3]
2 [2]
3 [2, 3]
3 [3]
8
```

## Why

```text
go(0) []
├── go(1) [1]
│   ├── go(2) [1, 2]
│   │   └── go(3) [1, 2, 3]
│   └── go(3) [1, 3]
├── go(2) [2]
│   └── go(3) [2, 3]
└── go(3) [3]
```

The nodes with `start = 3` are leaves: `range(3, 3)` is empty. Each subset appears once because a child only adds items to the **right** of the last chosen one, so `[2, 1]` is never built. For 4 items there are `2^4 = 16` nodes, so 16 lines plus the count.
