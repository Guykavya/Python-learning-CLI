## Approach

Follow the two heaps round by round. Only the order of pops matters, so track the stick lengths as a sorted list.

## Expected output

```text
smallest first
join 2 + 3 = 5, total 5
join 4 + 5 = 9, total 14
join 6 + 9 = 15, total 29
largest first
join 6 + 4 = 10, total 10
join 10 + 3 = 13, total 23
join 13 + 2 = 15, total 38
totals: 29 38
```

## Why

| rule | sticks before | joined | cost | total |
|---|---|---|---|---|
| smallest | 2 3 4 6 | 2 + 3 | 5 | 5 |
| smallest | 4 5 6 | 4 + 5 | 9 | 14 |
| smallest | 6 9 | 6 + 9 | 15 | 29 |
| largest | 6 4 3 2 | 6 + 4 | 10 | 10 |
| largest | 10 3 2 | 10 + 3 | 13 | 23 |
| largest | 13 2 | 13 + 2 | 15 | 38 |

In the largest-first run, the first popped is the biggest, so `a` is the larger stick (`6 + 4`, not `4 + 6`). The new stick 10 is the largest at once, so it is picked again: the 6 and the 4 are paid for three times. In the smallest-first run the long sticks are paid for the fewest times (6 only once): each stick's length counts once per join it takes part in, which is exactly its depth in the Huffman tree. Joining the smallest first is Huffman's rule, which the chapter proves optimal, so 29 is the cheapest possible total. For `[5, 5, 5, 5]` the smallest-first total is `10 + 10 + 20 = 40`, and no order is cheaper.

## Another way

Count each stick's depth instead of simulating: smallest first gives the tree `((2, 3), 4), 6` → depths `2: 3, 3: 3, 4: 2, 6: 1` → `2*3 + 3*3 + 4*2 + 6*1 = 29`. Largest first gives `((6, 4), 3), 2` → depths `6: 3, 4: 3, 3: 2, 2: 1` → `18 + 12 + 6 + 2 = 38`.
