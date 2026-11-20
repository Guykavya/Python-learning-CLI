## Approach

Chapter section 20: count in `[0, N]` digit by digit, then answer the range with `upto(hi) - upto(lo - 1)`.

- **State:** `go(pos, prev, tight, started)` = the number of ways to fill positions `pos..end` so that the whole number is a stepping number, given the last real digit `prev`, whether we are still on `N`'s prefix (`tight`), and whether the number has started.
- **Transition:** try every digit `d` up to the limit. A leading zero keeps `started` False and sets no `prev`. The first non-zero digit starts the number. After that, `d` is allowed only if `abs(d - prev) == 1`.
- **Base:** at the end, 1 (one complete number; "never started" is the number 0).

```python
import functools


def count_stepping(lo, hi):
    def upto(N):
        """Stepping numbers in [0, N]."""
        digits = list(map(int, str(N)))

        @functools.cache
        def go(pos, prev, tight, started):
            if pos == len(digits):
                return 1                       # one finished number (the number 0 if never started)
            limit = digits[pos] if tight else 9
            total = 0
            for d in range(limit + 1):
                now_tight = tight and d == limit
                if not started:
                    if d == 0:
                        total += go(pos + 1, -1, now_tight, False)   # still a leading zero
                    else:
                        total += go(pos + 1, d, now_tight, True)     # first real digit: anything goes
                elif abs(d - prev) == 1:
                    total += go(pos + 1, d, now_tight, True)
            return total

        return go(0, -1, True, False)

    return upto(hi) - (upto(lo - 1) if lo > 0 else 0)
```

**Why `started` is needed.** For `N = 100` the number 7 is filled as `0, 0, 7`. Without the flag, the second `0` would need a neighbour 1, and `7` would need a neighbour `0 ± 1`: the number 7 would not be counted. With the flag, the zeros are "not part of the number yet", and 7 is a single digit with no rule.

**Why it is fast.** `pos` takes at most 19 values, `prev` 11, `tight` and `started` 2 each: under 1,000 states, each trying at most 10 digits. `functools.cache` sits on the inner function, so every call of `upto` starts with a fresh memo (the digits of `N` are different each time).

## Complexity

`O(D * 10 * 10 * 4)` for `D` digits: a few thousand steps for `10**18`. Brute force needs `10**18` steps.

## Another way

Generate the stepping numbers instead of counting them: start from 1 to 9 and append `last ± 1` repeatedly (a BFS), keeping the numbers `<= hi`, and count those `>= lo` (plus 0 if `lo == 0`). There are only 1,143,889 stepping numbers up to `10**18`, so this works too, though it builds a million numbers where the DP visits under a thousand states. Digit DP is the general tool: with a property like "digit sum divisible by 7" there are far too many matching numbers to list, but the DP is just as fast.
