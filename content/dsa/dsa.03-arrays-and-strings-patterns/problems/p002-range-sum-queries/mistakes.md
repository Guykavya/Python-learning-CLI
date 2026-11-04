- Off by one: `p[r] - p[l]` drops the element at position `l`. The positions are 1-based and inclusive, so the cut is
  at `l - 1`.
- Mixing 0-based and 1-based: using `a[l:r]` or `p[r+1] - p[l]` copied from a 0-based formula. Decide which one your
  `p` uses and test the example by hand.
- Re-summing each range with a loop or `sum(...)`: correct but O(n * q), which times out here.
- Rebuilding the prefix list inside the query loop. Build it once.
