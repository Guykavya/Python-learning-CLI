## Hint 1

Start with `[3, 5, 8]`, target 8. Root `go(0, 8)`. Include 3: `go(1, 5)`. Include 5: `go(2, 0)`, found, stop. Exclude 5: `go(2, 5)`, which has two children with `i = 3`. Keep going and count every node.

## Hint 2

A negative remainder only matters if it appears at a node with `i < 3`: only then does the check stop children that would otherwise be created. A node with `i == 3` stops anyway.

## Hint 3

For `[5, 8, 3]`: including 5 and then 8 gives `go(2, -5)`. Without the check, that node still creates two children.
