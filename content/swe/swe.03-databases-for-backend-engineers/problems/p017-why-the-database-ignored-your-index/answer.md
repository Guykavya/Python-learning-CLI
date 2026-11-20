## Model answer

1. **Selectivity** is the fraction of rows a condition selects (or, the other way, how many rows it lets the database skip). `is_active = 1` selects 90% of the rows: it is **not selective**; it skips only 10%. A condition that selects a few rows out of a million is highly selective.
2. **Why the index loses.** Through an index, each of the 900,000 matches costs a lookup in the index plus a jump to the table row (often to a random page). A table scan reads the pages in order, which is far cheaper per row. When most rows match, doing 900,000 random jumps is slower than one sweep, so the planner (correctly) chooses the scan.
3. **The planner and `ANALYZE`.** The planner estimates the number of matching rows from statistics about the table and the index (how many rows, how many distinct values per index prefix) and chooses the cheaper plan. Without statistics it uses guesses. `ANALYZE` collects fresh statistics, so the estimates match reality; it can change the plan when the guess was wrong (for example when the planner expected the index to be selective).
4. **`is_active = 0`.** It matches 10% (100,000 rows), or fewer in other data: few enough that jumping from the index beats scanning everything, so the planner uses the index for that value.
5. **A better index.** Index what the page really needs. For "the 50 newest active users": a composite or partial index such as `CREATE INDEX idx_active_created ON users(created DESC) WHERE is_active = 1`, with `ORDER BY created DESC LIMIT 50`: the database reads 50 index entries. Or avoid the filter column and rely on the ordering index plus `LIMIT`. A boolean column alone is almost never worth an index.

**Checklist: your answer should mention**
- [ ] **selectivity**: 90% is not selective
- [ ] an index lookup per row (random access) can cost more than a **sequential scan**
- [ ] the planner uses **statistics** and estimated row counts; `ANALYZE` refreshes them
- [ ] the index is useful for the **rare** value (`is_active = 0`)
- [ ] a better index: **composite/partial** matching the real query (ordering and `LIMIT`)
