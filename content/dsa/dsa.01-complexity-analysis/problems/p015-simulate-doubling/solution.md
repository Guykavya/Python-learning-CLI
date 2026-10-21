## Walkthrough

| before item | size (full) | copies this time | new capacity | total copies |
|---|---|---|---|---|
| 2 | 1 | 1 | 2 | 1 |
| 3 | 2 | 2 | 4 | 3 |
| 5 | 4 | 4 | 8 | 7 |
| 9 | 8 | 8 | 16 | 15 |
| 17 | 16 | 16 | 32 | 31 |

Output:

```
grow before item 2 copy 1 capacity 2
grow before item 3 copy 2 capacity 4
grow before item 5 copy 4 capacity 8
grow before item 9 copy 8 capacity 16
grow before item 17 copy 16 capacity 32
items 17 copies 31 capacity 32
```

## Key idea

The copies form a doubling series `1 + 2 + 4 + ... + 16 = 31`, which is always less than twice the number of
items. For 1000 items the last growth copies 512, and the total is `1 + 2 + ... + 512 = 1023`. So `n` appends
cost `n` writes plus fewer than `2n` copies: O(n) in total, which is O(1) **on average per append**. That is
what "append is amortised O(1)" means. A single append can be expensive (the 17th copied 16 items), but the
expensive ones are rare enough that the average stays constant.

Real CPython grows by about one eighth plus a little each time, not by doubling, but any growth that is a fixed
fraction of the current size gives the same result: the copies add up to a constant times `n`.
