- **`agg("sum")` instead of `transform("sum")`.** That gives 3 numbers indexed by store, which do not line up with the
  8 lines; the division fills `NaN`.
- **Dividing by `lines["revenue"].sum()`.** That is the share of the whole shop, not of the line's store.
- **Merging totals back and losing the index.** After a merge the index is 0..n-1, not the input's labels.
- **`lines["share"] = ...`.** It changes the caller's frame.
