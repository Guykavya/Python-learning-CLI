- Starting `best = 0`. If every element is negative, no window reaches 0 and you print a sum that does not exist.
- Subtracting the wrong element: the one leaving is `a[r - k]`, not `a[r - k + 1]` or `a[r - 1]`.
- Off by one in the loop: `range(k, n)` gives `n - k` slides, so `n - k + 1` windows in total with the first one.
  Stopping at `n - 1` misses the last window.
- Re-summing each window with `sum(a[i:i + k])`: correct but O(n * k).
- Forgetting the case `k = n`: there is only one window, and the slide loop must not run.
