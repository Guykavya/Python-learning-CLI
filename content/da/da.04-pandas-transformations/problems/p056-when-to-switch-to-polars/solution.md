## Approach

Separate three things: what Polars *is* (no index, expressions, lazy plans, threads, Arrow), what one benchmark *can*
prove (very little beyond itself), and what decides a team's choice (size of data, the libraries around the analysis,
the people). Then end with the part that never changes. Compare with `answer.md` and tick the checklist.

## Code

```python
import polars as pl

lf = pl.LazyFrame({"store_id": ["S1", "S2", "S1"], "channel": ["online", "store", "online"],
                   "revenue": [10.0, 20.0, 5.0], "note": ["a", "b", "c"]})
plan = lf.filter(pl.col("channel") == "online").group_by("store_id").agg(pl.col("revenue").sum())
print(plan.collect().to_dicts())      # [{'store_id': 'S1', 'revenue': 15.0}]
# plan.explain() shows the optimised plan: the unused column `note` is never read
```

## Complexity

Not a question of O-notation: both libraries have the same complexity for the same operation. The differences are
constant factors (threads, compiled expressions) and memory (reading fewer columns, streaming).

## Another way

A fair decision document lists: the three slowest steps, their time in both libraries on real data (machine stated),
the memory peak, the libraries used downstream, and the cost of retraining the team. Then the answer is usually
"mostly pandas, Polars for the heavy pipeline step", not a full rewrite.
