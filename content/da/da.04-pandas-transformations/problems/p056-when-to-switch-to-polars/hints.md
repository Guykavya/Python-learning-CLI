## Hint 1

Re-read the comparison table of section 13.1 (index, style, execution, threads, missing values, memory format). For
each row ask: does it change *speed*, *safety*, or only *spelling*? Then ask what a single timing on one query can
prove about a whole workload.

## Hint 2

```text
1. no index (no alignment surprises); expressions; lazy plans + optimiser (fewer columns read, filters pushed down);
   many cores; one null; Arrow
2. one machine, one query, few repeats -> a hint; measure YOUR slowest steps, answers equal first
3. pandas: fits in memory, notebooks, libraries expect pandas (sklearn, statsmodels, plotting), team knows it
   Polars: big data / slow / out of memory, repeatable pipelines, files bigger than memory (scan + lazy)
   middle: heavy group-by/join in Polars, .to_pandas() the small result
4. grain, validate=, count rows, reconcile totals
```
