# pandas or DuckDB?

Chapter sections 9.1 and 9.6. A colleague asks: *"We already use pandas for everything. Why would I learn DuckDB, and when should
I not bother?"* In `answer.md`, in about 150 to 250 words, give an honest answer:

1. Name at least **three situations** where DuckDB (SQL on files or DataFrames) is the better tool, and **two** where pandas is.
2. Explain why you should **measure** instead of trusting a general claim "DuckDB is faster", and what exactly you would compare.
3. Say what to do so that the **logic of a metric lives in one place** when a team uses both tools.

## Example

A start: "They are not rivals. For a query that reads like a question about groups (joins, windows, top N per group) SQL is clearer.
When the data start in a Parquet file, DuckDB reads only the columns it needs, but..."
