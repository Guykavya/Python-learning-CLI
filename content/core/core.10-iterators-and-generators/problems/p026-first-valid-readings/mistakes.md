- `sum(sources, [])` or `list(source)` for each source: it reads every batch, even the ones you do not need.
- Testing `if r` instead of `r is not None`: then a valid reading of `0` is thrown away.
- `0 < r < 50`: the ends 0 and 50 are valid.
- In the nested-loop version, `break` only leaves the inner loop. The outer loop then opens the
  next source. Use `return`.
