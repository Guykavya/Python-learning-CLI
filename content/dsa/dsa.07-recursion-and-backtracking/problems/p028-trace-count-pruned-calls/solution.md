## Approach

Draw both trees, write `remaining` in every node, and count. The check stops a node only before it creates children, so it helps only when the target is overshot **high up** in the tree.

## Expected output

```text
(2, 13)
(2, 13)
(2, 13)
(2, 11)
```

## Why

`[3, 5, 8]`, target 8 (left = include):

```text
go(0, 8)
├── go(1, 5)
│   ├── go(2, 0)  found
│   └── go(2, 5) ── go(3, -3) | go(3, 5)
└── go(1, 8)
    ├── go(2, 3) ── go(3, -5) | go(3, 3)
    └── go(2, 8) ── go(3, 0) found | go(3, 8)
```

13 nodes and 2 subsets (`3 + 5`, `8`). The negative nodes have `i = 3` and are leaves anyway, so the check saves nothing: `(2, 13)` both times.
For `[5, 8, 3]`, including 5 and 8 gives `go(2, -5)` with `i = 2`. Without the check it creates the leaves `go(3, -8)` and `go(3, -5)`; with the check it stops: 13 nodes against 11. Big numbers early make overshooting happen high in the tree, where a cut removes more.
