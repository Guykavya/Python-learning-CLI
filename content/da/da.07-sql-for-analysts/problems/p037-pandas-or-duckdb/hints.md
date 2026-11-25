## Hint 1

Think of one task per tool: a join of three tables with a window function against a plot with a custom Python function. Then think of the size of the data: a few thousand rows against a file larger than memory.

## Hint 2

```text
paragraph 1: SQL wins for joins, windows, group questions, files on disk / Parquet, data larger than memory; pandas wins for reshaping, plotting, custom Python logic, small data already in memory
paragraph 2: speed depends on the query and the data; time your own query on your own data, several runs, best of them, and check the answers are equal
paragraph 3: one definition of each metric (one SQL file or one function), reused by notebooks and dashboards
```
