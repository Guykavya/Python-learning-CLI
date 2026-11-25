- **`p90=("delivery_days", p90())`.** Calling the function passes its *result*; `agg` needs the function itself.
- **`size` for `delivered`.** It counts undelivered orders too.
- **Dropping the undelivered rows before grouping with `dropna()` on the whole table.** That is fine for the
  statistics, but a region whose orders are all undelivered then disappears, and it must still be reported.
- **Taking the 9th of 10 sorted values.** That is 9, not 9.1: `quantile` interpolates between neighbours.
- **Filling missing days with 0.** An undelivered order did not take 0 days; it would pull the median down.
