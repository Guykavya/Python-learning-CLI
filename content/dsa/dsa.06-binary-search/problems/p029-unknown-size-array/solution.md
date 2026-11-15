## Approach

Exponential (doubling) search: the first phase finds an index `hi` whose value is at least `t` in about `log2(n)` questions; the second phase is an ordinary closed binary search on `[hi // 2, hi]`. Values past the end are huge, so they behave like "too large".

## Code

```python
t = int(input())


def ask(i):
    print("?", i, flush=True)
    return int(input())


hi = 1
while ask(hi) < t:
    hi *= 2
lo = hi // 2
ans = -1
while lo <= hi:
    mid = (lo + hi) // 2
    v = ask(mid)
    if v == t:
        ans = mid
        break
    elif v < t:
        lo = mid + 1
    else:
        hi = mid - 1
print("!", ans, flush=True)
```

## Complexity

O(log p) questions where `p` is the position of the target (or of the end), O(1) memory.

## Another way

Grow by a bigger factor (for example 4 or 10) when questions are cheap, or start from a known estimate. Doubling gives the best worst-case guarantee: at most twice the optimal number of questions.
