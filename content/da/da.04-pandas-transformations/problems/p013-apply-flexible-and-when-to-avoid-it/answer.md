## Model answer

1. **What `apply` does.** For every group, pandas builds the group's sub-table, makes a **Python call** to my function,
   and then glues the returned pieces (a scalar, a Series or a frame) into one result, guessing the shape. The work in
   my function may be fast, but the per-group overhead (object creation plus a Python call) is paid once per group.
   With 6 categories that is invisible; with 5,000 groups it dominates. The chapter measured a built-in `sum` against
   `agg(lambda)` (about 6× slower) and `apply(lambda)` (about 15× slower) on 5,000 groups (timings machine-specific).

2. **Faster replacements.**
   - Sum: `lines.groupby("category")["revenue"].sum()`. Built-in aggregations are **vectorised**: compiled code runs
     over all rows at once, no Python call per group.
   - Z-score: write the arithmetic around built-in **transforms**:
     `g = lines.groupby("category")["revenue"]` then `(lines["revenue"] - g.transform("mean")) / g.transform("std")`.
     Same numbers (check with `np.allclose`), measured about 20× faster in the chapter.
   - Top 2: **sort + head**: `lines.sort_values("revenue", ascending=False).groupby("category").head(2)`, or a
     `rank(...) <= 2` mask. Both keep the original columns and avoid the extra index level that `apply` adds.

3. **pandas 3 surprise.** The grouping columns are **excluded** from the sub-table the function receives, so
   `d["category"]` raises `KeyError`. The key is in `d.name`.

4. **When `apply` is right, and how to change code.** When the per-group logic really cannot be written with built-ins
   (several steps that depend on each other, a library call that needs the whole group) and the number of groups is
   modest. Before replacing anything: **measure first** on realistic data (correct first, then fast), keep the old
   version, and check that the new one gives the same result.

**Checklist: your answer should mention**
- [ ] a Python call per group (cost grows with the number of groups)
- [ ] built-in aggregations are vectorised
- [ ] `transform` with built-in names for per-row group statistics
- [ ] sort + head (or rank) for top-N per group
- [ ] grouping columns are not passed in pandas 3; use `d.name`
- [ ] measure first, then compare results
