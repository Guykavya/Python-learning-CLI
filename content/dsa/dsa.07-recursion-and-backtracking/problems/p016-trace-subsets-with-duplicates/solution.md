## Approach

Trace the calls in order. A `skip` happens when the loop is about to try a value that an earlier sibling at the **same** level already tried. A repeated value is fine when it is the first choice of its level (`i == start`), because then the previous equal value is already in the path.

## Expected output

```text
visit []
visit [1]
visit [1, 2]
visit [1, 2, 2]
skip i = 2 start = 1
visit [2]
visit [2, 2]
skip i = 2 start = 0
6
```

## Why

```text
go(0) []
├── i=0: go(1) [1]
│   ├── i=1: go(2) [1, 2]
│   │   └── i=2: go(3) [1, 2, 2]      (i == start, allowed)
│   └── i=2: skip (2 == nums[1], i > start = 1)
├── i=1: go(2) [2]
│   └── i=2: go(3) [2, 2]             (i == start, allowed)
└── i=2: skip (2 == nums[1], i > start = 0)
```

Without the skip rule the two cut branches would produce `[1, 2]` and `[2]` a second time (using the second 2). Six different subsets remain. With `i > 0`, the branch to `[1, 2, 2]` and `[2, 2]` would also be cut, which is wrong.
