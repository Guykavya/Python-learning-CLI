## Hint 1

If the answer is `d`, can you also place the cows with a smaller distance? So what does the set of "possible distances" look like on the number line?

## Hint 2

The possible distances form a block `1, 2, ..., D` and then fail. Search the **last** possible `d` in `[1, (max - min) // (c - 1)]`. The check is greedy: the first cow at the leftmost stall, then each next cow at the first stall `>= last + d`.

## Hint 3

```
sort stalls
lo, hi = 1, (stalls[-1] - stalls[0]) // (c - 1)
while lo < hi:
    mid = (lo + hi + 1) // 2        # round UP, because lo = mid below
    if can_place(mid): lo = mid
    else: hi = mid - 1
print(lo)
```
With `mid = (lo + hi) // 2` and `lo = mid`, the loop gets stuck when `hi = lo + 1`.
