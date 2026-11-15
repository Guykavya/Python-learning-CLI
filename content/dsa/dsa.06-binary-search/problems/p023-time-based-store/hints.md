## Hint 1

For one key the `set` times are sorted. Which element do you want for a `get` at time `t`: the first time `> t`, or the last time `<= t`? How are they related?

## Hint 2

Find `i = upper_bound(times, t)` (the number of times `<= t`). If `i == 0` there is no earlier `set`: print `NONE`. Otherwise the value is `values[i - 1]`.

## Hint 3

```
times = {}   # key -> list of times
vals = {}    # key -> list of values
set: append to both lists of the key
get: ts = times.get(key, [])
     lo, hi = 0, len(ts)
     while lo < hi:
         mid = (lo + hi) // 2
         if ts[mid] <= t: lo = mid + 1
         else: hi = mid
     print(vals[key][lo - 1] if lo > 0 else "NONE")
```
