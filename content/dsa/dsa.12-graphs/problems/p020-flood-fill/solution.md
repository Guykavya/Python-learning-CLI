## Approach

Simulate the queue. Paint on push, so that the grid itself is the "visited" record. The old colour is read once, before the start cell is painted.

## Expected output

```text
visit (0, 0)
visit (1, 0)
visit (0, 1)
visit (2, 0)
visit (2, 1)
visit (2, 2)
visit (3, 2)
**b.
*.ba
***b
b.*b
```

## Why

| visit | neighbours checked (up, down, left, right) | queued |
|---|---|---|
| (0, 0) | out, (1, 0) a, out, (0, 1) a | (1, 0), (0, 1) |
| (1, 0) | (0, 0) *, (2, 0) a, out, (1, 1) . | (2, 0) |
| (0, 1) | out, (1, 1) ., (0, 0) *, (0, 2) b | none |
| (2, 0) | (1, 0) *, (3, 0) b, out, (2, 1) a | (2, 1) |
| (2, 1) | (1, 1) ., (3, 1) ., (2, 0) *, (2, 2) a | (2, 2) |
| (2, 2) | (1, 2) b, (3, 2) a, (2, 1) *, (2, 3) b | (3, 2) |
| (3, 2) | (2, 2) *, out, (3, 1) ., (3, 3) b | none |

`(1, 3)` is an `a`, but its four neighbours are `.`, `b`, `b` and outside; it touches the region only **diagonally** (at `(2, 2)`), and flood fill uses four directions. If cells were painted on pop instead, the final grid would be the same, but a cell could sit in the queue twice (the "mark when you push" trap of section 3).

## Another way

A DFS with a stack, or recursion, paints the same region in a different visit order. Recursion is risky on big images: a 1000 x 1000 region is a million nested calls.
