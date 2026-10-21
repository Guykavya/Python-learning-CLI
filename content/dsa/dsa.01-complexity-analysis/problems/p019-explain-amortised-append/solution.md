The model answer is shown when you check. The ideas that must appear:

1. A full list must copy every item to a bigger block: that single append is O(n).
2. With doubling, copies are `1 + 2 + 4 + ... < 2n`, so `n` appends cost O(n) total: amortised O(1) each.
3. Growing by a fixed 10 slots copies about `n^2 / 20` items: O(n^2) total. Growth must be proportional to size.
4. `insert(0, x)` shifts all items: total `n(n - 1)/2`, O(n^2). The timings grow about 10x versus about 90x.
5. Amortised means average over a sequence; a single append can still be slow, which matters when every step
   has a deadline.
