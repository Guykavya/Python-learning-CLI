## Hint 1

You do not know `n`, but you may ask about any index. If `a[i] < t`, is it safe to look at `2 * i`? How do you know when you went too far?

## Hint 2

Start with `hi = 1` and double while `ask(hi) < t`. A reply `2147483647` is larger than any target, so it stops the loop too. Then the target, if present, is at an index in `[hi // 2, hi]`.

## Hint 3

```
hi = 1
while ask(hi) < t: hi *= 2
lo = hi // 2
while lo <= hi:                      # closed template on [lo, hi]
    mid = (lo + hi) // 2
    v = ask(mid)
    if v == t: answer mid
    elif v < t: lo = mid + 1
    else: hi = mid - 1
answer -1
```
Past-the-end replies are just big values: the binary search treats them as "too large".
