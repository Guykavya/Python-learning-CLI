## Hint 1

Count in `[0, N]` with a function `upto(N)`, then `count_stepping(lo, hi) = upto(hi) - upto(lo - 1)`, with `upto(-1)` taken as 0 when `lo = 0`.

For `upto(N)`, the state of `go(...)` needs:

- `pos`: the digit position being filled;
- `prev`: the last real digit placed (the next one must be `prev - 1` or `prev + 1`);
- `tight`: still equal to the prefix of `N`, so the next digit is at most `N`'s digit;
- `started`: whether a non-zero digit has been placed yet.

## Hint 2

While `started` is False, a `0` is a leading zero: it is not a digit of the number, so it puts no rule on the next digit. The first non-zero digit can be anything from 1 to the limit; after that, only `prev - 1` and `prev + 1` are allowed. At the end (`pos == len(digits)`), return 1: a number that never started is the number 0, which is a stepping number.

## Hint 3

```
@cache
go(pos, prev, tight, started):
    if pos == len(digits): return 1
    limit = digits[pos] if tight else 9
    total = 0
    for d in 0..limit:
        t = tight and d == limit
        if not started:
            total += go(pos+1, -1, t, False) if d == 0 else go(pos+1, d, t, True)
        elif abs(d - prev) == 1:
            total += go(pos+1, d, t, True)
    return total
upto(N) = go(0, -1, True, False)
```
