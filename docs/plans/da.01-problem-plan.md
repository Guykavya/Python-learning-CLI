# Problem plan: da.01 Analysis environment and descriptive statistics (30 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.01.p001` … `p030`, folder `pNNN-slug`.

**Mix:** 10 drill, 11 applied, 6 deep, 3 challenge. **Kinds:** 22 code, 5 trace, 3 explain.
**assessment:** explain = p013, trace = p003, fix = p026, build = p030.
**★ core set (write first, 12):** p001, p003, p009, p012, p013, p016, p019, p021, p023, p026, p028, p030.

**Testing notes**

- **Standard library only** (the chapter's offline rule: no NumPy/pandas/matplotlib until da.02). Learners use
  `statistics`, `csv`, `json`, `math`, `random`. Tests may use `statistics` as the second opinion.
- Data reach the solution as lists or dicts (R1). Problems that read a CSV get a **path the test wrote into
  `tmp_path`** (the messy-file rows are inline in the test, copied from Ch. 7.2's style). Never a fixture the
  learner must open from `my-work/`.
- Datasets: small inline lists for hand-checked numbers. For property tests, generate with
  `random.Random(seed)` inside the test and compute the expected value with `statistics` or an obvious slow
  version; never hard-code numbers that came from the chapter's `datasets.py` generators (R3).
- Notebook problems work on **notebook dicts** (the JSON of Ch. 2.5) passed in by the test. The solution never
  reads a learner-saved `.ipynb` (not copied by the runner, R1). The test may check results with
  `nbformat.validate(nbformat.from_dict(nb))` (nbformat 5.11 is installed). Measured 2026-11-18: a `nbformat_minor: 5`
  notebook **without cell `id`s** validates but emits a missing-id warning that will become an error, so p002
  requires ids.
- Percentile definitions: always name the method in `problem.md` (nearest-rank, inclusive, exclusive as in Ch. 12.2).
  Measured: `statistics.quantiles([15,20,35,40,50], n=4)` → `[17.5, 35.0, 45.0]` (exclusive, the default),
  `method="inclusive"` → `[20.0, 35.0, 40.0]`.
- Float answers: `pytest.approx(rel=1e-9)`; printed answers in traces use `f"{x:.2f}"`.

## A. Questions and notebooks (Ch. 1–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Read the code out of a notebook | drill | code | `code_cells(nb) -> list[str]`; joins each cell's `source` (a list of lines **or** one string, both are legal); skips markdown and raw cells; empty notebook → `[]` |
| 2 | Build a valid notebook | drill | code | `make_notebook(cells)` from `[("markdown", "# Title"), ("code", "x = 1")]`; `nbformat 4`, `nbformat_minor 5`, unique cell `id`s, code cells have `outputs: []` and `execution_count: None`; test runs `nbformat.validate` and checks no warning |
| 3 | Trace the hidden state | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` the chapter's `MiniKernel` (Ch. 3.1, code copied into `problem.md`) runs 5 cells **out of order**, one of them redefining a variable, then `restart()` and one more cell (which raises `NameError`); write the printed lines |
| 4 | Notebook or script? | drill | explain | six tasks (explore a new CSV, a nightly report, a reusable parser, a chart for a meeting, a function with tests, a one-off check); pick notebook or script and say why; checklist: "hidden state", "run top to bottom", "import from a module", "tests", "version control diff" |
| 5 | Strip outputs before sharing | applied | code | `strip_outputs(nb)` returns a **new** notebook with `outputs: []`, `execution_count: None` and no `metadata.execution`; the input dict is unchanged (test keeps a `copy.deepcopy` and compares; message: "you changed the caller's notebook: the mutation trap of Ch. 3.4") |
| 6 | Was it run top to bottom? | applied | code | `run_order_problems(nb)` lists indexes of code cells that were never run (`None`) or whose `execution_count` is not strictly increasing; a clean "Restart and run all" notebook → `[]` |

## B. Kinds of data and reading a messy CSV (Ch. 5–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 7 | Frequency table for a category | drill | code | `frequency_table(values)` → list of `(value, count, percent)` sorted by count desc, then value; `None` and `""` counted as `"(missing)"`; percents rounded to 1 decimal and summing to about 100 |
| 8 | A median for an ordinal scale | applied | code | `ordinal_median(responses, order)` (`order = ["strongly disagree", …, "strongly agree"]`); odd count → the label; even count with two different middle labels → a tuple of both (Ch. 6.4: the mean of ranks is suspect); unknown label → `ValueError` naming it |
| 9 | A forgiving number parser | applied | code | `parse_number(text)` with the rules of Ch. 7.4 copied into `problem.md` (thousand separators, spaces, currency sign, `n/a`/`-`/empty → `None`, scientific notation); a table of 15 cases; message names the case |
| 10 | What does `csv` really read? | applied | trace | `⚠ HAND-TRACE` `csv.reader` over 6 inline lines: a quoted comma, a doubled quote `""`, a trailing space, an empty line, a short row; print `len(row)` and `row` for each |
| 11 | Load one column, and say what was dropped | applied | code | `load_column(path, column, low=None, high=None, dedupe_on=None)` → `(values, report)`; the test writes the CSV into `tmp_path`; report counts per reason (`"unparseable"`, `"out_of_range"`, `"duplicate"`); missing column → `KeyError` with the column name; `encoding="utf-8"`, `newline=""` |

## C. The centre (Ch. 8–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 12 | Mean, median and mode from scratch | drill | code | `mean`, `median`, `modes` without `statistics`; even/odd length; `modes` returns all tied values sorted; empty list → `ValueError` with a clear message; compared with `statistics` on 50 seeded lists |
| 13 | When the median beats the mean | applied | explain | `assessment = "explain"`. Given 9 incomes plus one very rich household (numbers in `problem.md`), explain which centre to report and why, with the two numbers; checklist: "skew", "outlier pulls the mean", "typical household", "the mean is a share, the median is a person", "report both when in doubt" |
| 14 | Which centre minimises which loss? | deep | code | `total_loss(values, c, kind)` for `"squared"` and `"absolute"`, and `best_centre(values, kind)` searching the candidate points; test: squared → the mean; absolute → any point between the two middle values (test checks the **loss** equals the median's, not the exact point, so an even-length list does not fail a correct answer) |
| 15 | Trimmed mean | drill | code | `trimmed_mean(values, proportion=0.1)` cutting `floor(n * proportion)` from each end (Ch. 9.1); `proportion=0` → mean; `>= 0.5` → `ValueError`; input list not sorted in place |
| 16 | Weighted, geometric and harmonic means | applied | code | three functions; growth `[+10%, -10%]` → geometric mean of factors below 1; average speed over equal distances → harmonic; zero or negative → `ValueError`; compared with `statistics.geometric_mean/harmonic_mean/fmean(weights=)` |
| 17 | Trace `compare_centres` | drill | trace | `⚠ HAND-TRACE` the chapter's `compare_centres` and `skew_hint` (Ch. 10.6, code in `problem.md`) on three short lists (symmetric, right tail, left tail); printed with 2 decimals |
| 18 | Variance: population or sample? | drill | code | `variance(values, ddof)` and `stdev`; `ddof=1` with one value → `ValueError`; compared with `statistics.pvariance/variance` on seeded lists |

## D. Spread, percentiles and outliers (Ch. 11–13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Spread that resists outliers | applied | code | `describe_spread(values)` → dict `range, sd, iqr, mad, cv`; IQR with the **inclusive** method (stated); adding one huge value changes `sd` a lot and `iqr`/`mad` little (property test); `cv` with mean 0 → `None` |
| 20 | Three percentiles by hand | deep | trace | `⚠ HAND-TRACE` nearest-rank, inclusive and exclusive 25th/50th/90th percentile of `[15, 20, 35, 40, 50]` with the chapter's three functions (Ch. 12.2, code in `problem.md`); 2 decimals. Check against the measured `statistics.quantiles` values in Testing notes |
| 21 | Three percentile functions | applied | code | `percentile_nearest_rank`, `percentile_inclusive`, `percentile_exclusive(values, p)`; checked against `statistics.quantiles(n=100, method=…)` for integer `p`; sanity checks of Ch. 12.3: monotone in `p`, between min and max, p=50 equals the median for the inclusive method; exclusive method with too few values → `ValueError` |
| 22 | Percentile rank with ties | drill | trace | `⚠ HAND-TRACE` the chapter's `percentile_rank` (count below + half of equal, Ch. 12.5) for 4 scores in a list with ties; one line each |
| 23 | When the z-score hides the outlier | deep | code | `flag_iqr(values, k=1.5)` and `flag_z(values, t=3)` return indexes; test 1: an ordinary outlier both catch; test 2: **two** huge values in 12 points inflate the sd so `flag_z` misses them and `flag_iqr` catches them (message explains masking); constant list → no flags, no division by zero |
| 24 | Histogram counts | applied | code | `histogram_counts(values, bins, low=None, high=None)` → list of `(left, right, count)`; the maximum value lands in the **last** bin (message: "half-open bins drop the max"); counts sum to `n` when no range is given; values outside a given range are ignored and counted in a returned `outside` number |

## E. Shapes, misleading summaries, correlation (Ch. 14–16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Skewness with a sign you can trust | deep | code | `skewness(values)` with the Ch. 14.5 formula (stated); symmetric data → about 0; right tail → positive; a mirrored list → the exact negative; fewer than 3 values or zero spread → `ValueError` |
| 26 | Fix the summary function | deep | code | `assessment = "fix"`. Given `summarise(values)` with three bugs: sorts the caller's list in place (Ch. 3.4), uses `n` for the sample sd, and an off-by-one median for even lengths. Tests: input unchanged, sd equals `statistics.stdev`, even-length median, a test for each bug with a message naming it |
| 27 | Simpson's paradox detector | challenge | code | `rates_by_group(rows)` with rows `(group, treatment, success)`; returns per-group and overall success rates per treatment, and `paradox: bool` when every group prefers A but the total prefers B; the test uses the kidney-stone-style numbers from Ch. 15.1 and a no-paradox case |
| 28 | Same summary, different data | deep | explain | four datasets with the same mean and sd (given as text histograms in `problem.md`); explain what the summary hides and which extra numbers or picture reveal it; checklist: "shape", "bimodal", "outlier", "plot first", "five-number summary", "averaging averages" |
| 29 | A reproducibility manifest | challenge | code | `manifest(values, seed, params)` → dict with `sha256` of the values (as canonical JSON), `seed`, `params`, `python` version, `n`; JSON-serialisable; the same inputs give the same hash; param order does not change it (`sort_keys`); a changed value changes it |
| 30 | Build `describe()` and its report | challenge | code | `assessment = "build"` (the project slice of Ch. 17/19). `describe(values)` ignores `None`, returns `n, missing, mean, median, sd, min, q1, q3, max, iqr, skew_hint`; `report(name, values, unit="")` returns the text report including one advice line ("report the median" when the gap rule of Ch. 10.6 fires). Tests compare every number with `statistics` and check the advice on a skewed and a symmetric list; no hints file beyond 2 general hints (build rule) |

## Counts check

Tiers: drill 1, 2, 3, 4, 7, 12, 15, 17, 18, 22 = 10 · applied 5, 6, 8, 9, 10, 11, 13, 16, 19, 21, 24 = 11 ·
deep 14, 20, 23, 25, 26, 28 = 6 · challenge 27, 29, 30 = 3. Total 30.
Kinds: trace 3, 10, 17, 20, 22 = 5 · explain 4, 13, 28 = 3 · code 22.
Assessments: explain p013, trace p003, fix p026, build p030 (one each).

## Risks and open questions

- The chapter's `compare_centres`, `skew_hint`, `percentile_*`, `MiniKernel` and `parse_number` rules must be
  copied **exactly** into the trace/problem statements; re-read Ch. 3.1, 7.4, 10.6, 12.2, 12.5 when writing p003,
  p009, p017, p020, p022.
- p010: the `csv` module's handling of a short row and an empty line (empty line → `[]`) must be checked by running.
- p027 numbers must reproduce the paradox; recompute them in the test, do not trust memory.
- Python `random.Random(seed)` streams are stable across versions for `random()`/`randint`, but tests still compute
  expected values with `statistics`, never hard-code them.
