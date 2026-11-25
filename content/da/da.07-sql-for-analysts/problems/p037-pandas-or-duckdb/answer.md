## Model answer

They are not rivals; the tool should match the task. **DuckDB is better** when the question reads like SQL (joins, windows,
top-N per group, retention and funnels), when the data **start in a file** (it queries Parquet directly and reads only the
columns the query names), and when the data are **larger than memory** (it reads in pieces where `pd.read_parquet` would fail).
**pandas is better** for reshaping and cleaning with Python logic, for plotting, for small data already in memory, and when a step
needs an arbitrary Python function.

Do not trust "DuckDB is faster" without **measuring** your own query on your own data: take the best of several runs on the same
machine and check that both give the same answer. In the chapter's test a groupby on a DataFrame was close between the tools, while
querying a Parquet file directly was many times faster; the difference came from reading fewer columns, not from magic.

When a team uses both, keep **one source of truth** for each metric: one SQL file or one function that every notebook and
dashboard calls, with the definition in a comment, so that a change is made once and the reports cannot disagree.

**Checklist: your answer should mention**
- [ ] data fits in memory (or not): pandas for small in-memory data, DuckDB when larger or on files
- [ ] SQL readability for joins, windows and group questions
- [ ] Parquet scans read only the needed columns
- [ ] measure on your own data (several runs, check the answers)
- [ ] one source of truth for the logic of a metric
