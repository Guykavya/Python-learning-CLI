## Approach

Simulate the heap. Order entries by weight, then by tie number. The first pop is the left child, the second pop the right child.

## Expected output

```text
join b(1, tie 1) + d(1, tie 3) -> 2, tie 6
join c(2, tie 2) + r(2, tie 5) -> 4, tie 7
join bd(2, tie 6) + a(3, tie 0) -> 5, tie 8
join e(3, tie 4) + cr(4, tie 7) -> 7, tie 9
join bda(5, tie 8) + ecr(7, tie 9) -> 12, tie 10
a 01
b 000
c 110
d 001
e 10
r 111
cost: 30
```

## Why

Start (ties in alphabetical order): `a(3,0) b(1,1) c(2,2) d(1,3) e(3,4) r(2,5)`.

| round | heap before (weight, tie) | popped (left, right) | pushed |
|---|---|---|---|
| 1 | a(3,0) b(1,1) c(2,2) d(1,3) e(3,4) r(2,5) | b(1,1), d(1,3) | bd(2,6) |
| 2 | a(3,0) c(2,2) e(3,4) r(2,5) bd(2,6) | c(2,2), r(2,5) | cr(4,7) |
| 3 | a(3,0) e(3,4) bd(2,6) cr(4,7) | bd(2,6), a(3,0) | bda(5,8) |
| 4 | e(3,4) cr(4,7) bda(5,8) | e(3,4), cr(4,7) | ecr(7,9) |
| 5 | bda(5,8) ecr(7,9) | bda(5,8), ecr(7,9) | root(12,10) |

- **Round 2:** `c`, `r` and `bd` all weigh 2. The tie numbers are 2, 5 and 6, so `c` and `r` are joined and `bd` waits. With a rule that preferred joined trees, `bd` would be joined in round 2 and the codes would change.
- **Round 3:** `a` and `e` both weigh 3; `a` has tie 0, `e` has tie 4, so `a` is joined with `bd`. Note that `bd` (weight 2) is popped first, so it is the **left** child and `a` is the right child.

Codes, from the tree `(((b, d), a), (e, (c, r)))`: `b = 000`, `d = 001`, `a = 01`, `e = 10`, `c = 110`, `r = 111`. The cost is `3*2 + 1*3 + 2*3 + 1*3 + 3*2 + 2*3 = 30`, the same as the sum of the joins `2 + 4 + 5 + 7 + 12 = 30`.

The cost does **not** depend on the tie rule (every Huffman tree for these weights costs 30), but the codes do. That is why a test of exact codes must fix the tie rule (chapter section 13, "Why the tie-breaker also makes the output reproducible").

## Another way

Without a heap: keep the entries in a list sorted by `(weight, tie)` and take the first two each round, as in the chapter's hand-traced example. It gives the same joins, because the heap pops in exactly that order.
