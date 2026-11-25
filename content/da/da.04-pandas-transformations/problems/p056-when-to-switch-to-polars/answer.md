## Model answer

1. **What is different.** Polars has **no index**: rows are positions, so the alignment surprises and repeated labels
   of pandas cannot happen. It is written with **expressions** (`pl.col("revenue").sum()`) inside a few verbs, which
   Polars can run in parallel on several cores. It can be **lazy**: a `LazyFrame` records a plan, and the optimiser
   trims it before `collect()` runs it once, reading only the needed columns and filtering early (the chapter's
   `explain()` showed "3/9 COLUMNS"). It has one `null` for every type and stores data in Arrow format. The index and
   the single `null` mostly mean fewer bugs; threads, lazy optimisation and `scan_parquet` mean speed and less memory.

2. **What the measurement shows.** One query, on one machine, with a few repetitions: Polars was about 1.5 times faster
   on that group-by. It does not show "10 times faster", it does not say anything about our joins, reshapes, string
   cleaning or file reading, and the ratio changes with data size, cores, dtypes and versions; sometimes pandas wins.
   To decide, **measure on your data**: take the team's slowest real steps, write them in both libraries, check first
   that the answers are equal (sort, then compare), and then time them several times on realistic sizes.

3. **When to switch.** Stay with **pandas** for exploration in notebooks, tables that fit comfortably in memory, and
   whenever the rest of the work needs the **pandas ecosystem** (scikit-learn, statsmodels, plotting libraries) or the
   team already knows it well. Choose **Polars** when tables are big enough that pandas is slow or runs out of memory,
   for repeatable pipelines where lazy plans and strict types help, and for files larger than memory (`scan_parquet`
   with the streaming engine). The middle way: do the heavy group-by and join in Polars, then `.to_pandas()` the
   *small* result for plots and models. Convert after reducing, never before.

4. **What does not change.** The concepts: know the grain of every table, say the relationship of every join
   (`validate=` exists in both), count rows before and after, sort before comparing, and reconcile every breakdown
   with its total. A rewrite that skips these checks is fast and wrong.

**Checklist: your answer should mention**
- [ ] measure on your data (one benchmark is a hint; answers equal first)
- [ ] lazy optimisation (plan, optimiser, read only needed columns)
- [ ] expressions (and parallel execution on several cores)
- [ ] pandas ecosystem (libraries expect pandas; team knowledge)
- [ ] no index (fewer alignment bugs)
- [ ] the habits that stay: validate, row counts, reconcile
