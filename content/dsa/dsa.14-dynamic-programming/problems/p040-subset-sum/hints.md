## Hint 1

Let `f[s]` be True when some subset of the numbers processed so far sums to `s`. Before any number, only `f[0]` is True (the empty subset). Processing a number `x`: every sum `s` that was reachable stays reachable, and `s + x` becomes reachable too. Seen from `s`: `f[s] = f[s] or f[s - x]`.

## Hint 2

Each number may be used once, so `f[s - x]` must be the value from **before** `x` was processed: loop `s` downwards, from `target` to `x` (the 0/1 knapsack rule of p036). Going upwards, `[2]` with target 4 becomes True (2 used twice).

```
f = [False] * (target + 1); f[0] = True
for x in nums:
    for s from target down to x:
        if f[s - x]: f[s] = True
return f[target]
```

## Hint 3

For the bonus: keep one integer `bits`, starting at `1` (only bit 0 set: sum 0 is reachable). `bits << x` moves every reachable sum `s` to `s + x`. So `bits |= bits << x` is the whole update for number `x`. The answer is bit `target`: `(bits >> target) & 1`. Optional: keep `bits` small with `bits &= (1 << (target + 1)) - 1`, since sums above `target` are never needed.
