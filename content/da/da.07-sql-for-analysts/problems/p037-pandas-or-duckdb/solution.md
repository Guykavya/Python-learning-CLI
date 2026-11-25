## Approach

The honest answer is "both", with reasons. The chapter timed a 3-million-row groupby: the two tools were close for a DataFrame already in memory, and DuckDB was about eight times faster when querying a Parquet file directly (those timings are machine-specific, read the ratio).

## Code

Nothing to run. If you want a measurement habit, this is the shape:

```python
best = min(timeit_once(query) for _ in range(3))     # best of several runs
assert a.equals(b)                                    # and check the answers agree
```

## Complexity

Not applicable.

## Another way

Use each at its strength in one notebook: DuckDB for the heavy relational part and Parquet scans, then `.df()` into pandas for plotting and Python-specific steps.
