- **Optimising before profiling.** On the sample data, `find_product` looks guilty but the
  `BY MONTH` re-parsing is three quarters of the time. On other data it is the other way round.
  Profile on data shaped like the real thing, and on more than one shape.
- **Fixing one hot spot and stopping.** Each of the three dominates on a different kind of input;
  a program is only as fast as its slowest remaining part.
- **Changing the output while speeding up.** Ranking ties by name instead of id, sorting months
  as numbers, a missing final newline, or counting skipped orders in the revenue all break the
  report. Compare against the original after every change.
- **Caching `find_product` with `lru_cache`.** The product list is unhashable, and even a
  hand-made cache keyed by `id(products)` is a workaround for the real fix: a dict index.
- **Removing the per-month loop but still calling `strptime` 12 times per order elsewhere.**
  Count the calls in the profile after the fix: it should be at most one parse per order.
- **Keeping `sorted(...)` inside the ranking loop and only removing `index`.** The sort is the
  expensive part.
- **Timing a single run on tiny data.** Use big inputs, several repeats, and the minimum.
