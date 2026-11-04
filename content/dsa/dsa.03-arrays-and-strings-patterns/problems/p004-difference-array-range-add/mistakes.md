- Size `n + 1` for `d`: then `d[r + 1]` crashes when `r = n`. Use `n + 2`, or skip the minus when `r = n`.
- Putting the minus at `d[r]` instead of `d[r + 1]`: the last position of the range loses its `v`.
- Adding the running total to `a` but forgetting to carry it: `a[i] += d[i]` without the running sum adds `v` only
  at position `l`.
- Updating every cell of every range: correct, but O(n * q) and too slow for 200000 updates over long ranges.
- Mixing 1-based `d` indices with 0-based `a` indices: `a[i - 1] += run` for `i` from 1 to `n`.
