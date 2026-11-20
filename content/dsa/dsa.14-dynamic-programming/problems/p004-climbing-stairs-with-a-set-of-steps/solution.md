## Approach

- **State:** `f(i)` = the number of move sequences that land exactly on step `i`.
- **Transition:** group the sequences by their last move `s`. Before it, the climber stood on `i - s`, reached in `f(i - s)` ways. Different last moves give different sequences, so `f(i) = sum of f(i - s)` over the steps `s <= i`.
- **Base:** `f(0) = 1` (the empty sequence).
- **Answer:** `f(n)`. **Order:** increasing `i`.

This is `coin_sequences` from chapter section 7: amounts (here, stairs) outside, moves inside, because order matters.

```python
MOD = 10**9 + 7


def count_ways(n, steps):
    f = [0] * (n + 1)
    f[0] = 1
    for i in range(1, n + 1):
        total = 0
        for s in steps:
            if s <= i:
                total += f[i - s]
        f[i] = total % MOD
    return f[n]
```

## Complexity

`O(n * k)` time for `k` steps, `O(n)` space.

## Another way

Top-down: `go(i) = sum(go(i - s) for s in steps if s <= i)` with a memo. It is correct, but `i` can go down by 1 at a time, so the recursion is up to `n` deep and fails at `n = 10**4`. If you only need `f(n)`, a rolling window of the last `max(steps)` values is enough (chapter section 6, "The window of a look-back DP").
