# Problem plan: da.05 Data cleaning and missing-data reasoning (40 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.05.p001` … `p040`, folder `pNNN-slug`.

**Mix:** 13 drill, 14 applied, 10 deep, 3 challenge. **Kinds:** 30 code, 6 trace, 4 explain.
**assessment:** explain = p028, trace = p032, fix = p039, build = p040.
**★ core set (write first, 16):** p002, p005, p010, p016, p020, p024, p026, p027, p028, p030, p032, p034, p035, p037, p039, p040.

**Testing notes**

- The chapter's worlds: a messy **survey** with a known truth (`make_survey`, Ch. 1.2), a **population** where everything
  is known (`make_population`, Ch. 8.2) and the **air-quality** project (`make_air`, Ch. 13). Tests use small inline
  frames for exact checks, and a seeded generator in `conftest.py` (a trimmed copy of the chapter's) for the
  missing-data simulations (R1, R3).
- **Known truth is the key testing idea of this module:** the test keeps the clean truth, makes a messy copy, passes
  the messy copy to the solution and compares the result with the truth (Ch. 12.3).
- Missing-data simulations (p027, p029, p030) never assert exact numbers from random draws. They assert a **direction
  with a margin** (e.g. "complete-case mean is at least 5% above the truth under MNAR") on n ≥ 5,000 and check it
  holds on 3 seeds when the problem is written.
- Regex: every pattern problem has a table of 10–15 cases including the edge cases named in the chapter. p014 runs the
  solution in a subprocess with a 2-second limit on an adversarial input.
- pandera **0.36** with pandas 3.1.1 (measured 2026-11-18): `import pandera.pandas as pa` (the chapter's form);
  eager `validate` raises `pa.errors.SchemaError`; `validate(lazy=True)` raises `pa.errors.SchemaErrors` whose
  `failure_cases` has columns `schema_context, column, check, check_number, failure_case, index`; check names print as
  `in_range(18, 75)`, `isin(['Pune', 'Delhi'])`, `field_uniqueness`. `DataFrameModel` works.
- Also measured: `str.replace(r"\D", "", regex=True)` on `"+91 98765-43210"` → `"919876543210"`; `str.extract` with
  named groups returns a frame with those column names.
- Traces print `.tolist()`, `int()`, `round(float(x), 2)`; never a frame repr (R3).

## A. Cleaning as analysis: the audit (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | A change log | drill | code | `log_step(log, name, before, after, note="")` appends `{step, rows_before, rows_after, dropped, note}`; `show_log(log)` returns the text table; dropped never negative |
| 2 | The audit | applied | code | `audit(df)` → one row per column: dtype, missing, unique, top values, and `suspect_text` (count of values in a number-like text column that do not parse); checked against direct pandas calls |
| 3 | Four rules before any code | drill | explain | Ch. 1.1: keep the raw data, log every step, decide with the question in mind, check against something known; checklist with those four + "never fix by hand in the file" |

## B. Inconsistent formats and fake values (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 4 | One city, five spellings | drill | code | `standardise_city(s, mapping)` strips, case-folds, then maps; unmapped values returned as a sorted list; NA stays NA |
| 5 | Incomes stored as text | applied | code | `parse_income(s)` with the rules of Ch. 3.2 copied into `problem.md` (`"45k"`, `"₹45,000"`, `"45000/-"`, `"forty"` → NA, …); 15 cases |
| 6 | Sentinel codes | drill | code | `replace_sentinels(df, codes)` with `codes = {"age": [-1, 999], "income": [0]}` → NA; returns the count replaced per column; other columns untouched |
| 7 | Three date formats in one column | applied | code | `parse_signup(s)` detects the format of each value by its pattern (Ch. 3.4) and parses with that format; impossible dates → NA and listed |
| 8 | Units | drill | code | `to_kg(values, units)` for `g`, `kg`, `lb` (factor stated); unknown unit → `ValueError` naming it; case and spaces tolerated |
| 9 | What sentinels do to a mean | drill | trace | `⚠ HAND-TRACE` mean and median of 8 ages containing `-1` and `999`, before and after replacing them with NA; 2 decimals |

## C. Regex inside pandas (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Phone numbers | applied | code | `clean_phone(s)`: keep digits, drop a leading `91`/`0` when the rest is 10 digits, require a first digit 6–9 (Ch. 4.2 rules), else NA; 15 cases |
| 11 | Emails: clean, then check | drill | code | `clean_email(s)` → lower-cased, stripped address or NA if it fails the simple pattern of Ch. 4.3; `"Asha@Example.COM "` → `"asha@example.com"` |
| 12 | Pull pieces out of a code | applied | code | `split_product_code(s)` with `str.extract` and named groups: `"EL-2024-0042"` → `category`, `year` (int), `number` (int); non-matching → NA row |
| 13 | Regex or plain text? | deep | trace | `⚠ HAND-TRACE` `str.replace(".", "", regex=False)` vs `regex=True`, `str.contains("+1", regex=False)`, `str.count(r"\d")`, on 3 short strings; one call raises (print the exception class name) |
| 14 | A regex that never finishes | deep | code | `is_valid_ref(s)` for references like `AB-12-34-56`; the naive pattern with nested quantifiers hangs on a 40-character near-miss; the test runs the solution in a subprocess with a 2-second limit (Ch. 4.5) |

## D. Duplicates (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Exact duplicates | drill | code | `drop_exact_duplicates(df)` → `(clean, n_removed)`; rows that differ only in case are **not** exact duplicates |
| 16 | Duplicates by key | applied | code | `dedupe_by_key(df, key, order_by)` keeps the latest row per key; returns the removed rows for the log |
| 17 | Which copy survives? | deep | code | `best_copy(df, key)` keeps the **most complete** row (most non-missing values), ties → latest `updated_at`; checked against a loop |
| 18 | Near duplicates | challenge | code | `similar_names(names, threshold=0.85)` with `difflib.SequenceMatcher` after normalising (Ch. 5.5); returns sorted pairs; does not compare a name with itself; n = 300 within budget |
| 19 | `keep="first"`, `"last"`, `False` | drill | trace | `⚠ HAND-TRACE` rows kept by `drop_duplicates(subset="id", keep=…)` for the three options on 7 rows; print the kept `row_id` lists |

## E. Outliers (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | Three rules for suspects | applied | code | `flag_iqr(x, k)`, `flag_z(x, t)`, `flag_mad(x, t)` returning boolean Series aligned to `x`; NA never flagged; constant column → no flags |
| 21 | Domain rules first | drill | code | `flag_impossible(df, rules)` with `rules = {"age": (0, 120), "income": (0, None)}` → boolean frame plus count per rule |
| 22 | What to do with a suspect | applied | code | `outlier_strategies(s, flags)` → dict of mean and median after keep, remove, cap at the fence, and flag-only; shows that the choice moves the mean |
| 23 | Outlier or best customer? | applied | explain | three suspects (a ₹9,00,000 order, age 140, a sensor stuck at the same value for 8 hours); decide and justify; checklist: "domain knowledge first", "flag, do not delete silently", "check the source", "report the effect" |

## F. Missing values: the mechanics (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Four kinds of "missing" | drill | code | `to_missing(df, tokens=("", "NA", "n/a", "-"))` turns blanks, whitespace-only text and tokens into real NA; numbers untouched; count per column |
| 25 | Missing values do not equal anything | drill | trace | `⚠ HAND-TRACE` `s == np.nan`, `s.isna()`, `(s > 2).tolist()` with NA, `s.sum()`, `s.mean()`, `value_counts(dropna=False)` on a 5-value Series |
| 26 | Measure missingness by group | applied | code | `missing_profile(df, by, col)` → per group: rows, missing, rate; sorted by rate desc; a group with no missing → rate 0 |

## G. Why values are missing (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Does missingness depend on what I can see? | deep | code | `missingness_gap(df, col, other)` → mean of `other` where `col` is missing vs present, and the difference; on simulated MAR data the gap is clearly non-zero, on MCAR data close to 0 (margins, 3 seeds) |
| 28 | MCAR, MAR, MNAR | deep | explain | `assessment = "explain"`. Explain the three mechanisms with one example each from the survey, and what each does to a complete-case mean; checklist: "missing completely at random", "depends on an observed column", "depends on the missing value itself", "bias", "cannot be proven from the data alone" |
| 29 | Make the data go missing | deep | code | `simulate_missing(pop, mechanism, rate, rng)` for `"MCAR"`, `"MAR"` (by age), `"MNAR"` (high incomes hide more); returns a copy; rate within ±2 points of the target; MNAR complete-case mean below the truth by a margin |

## H. When dropping or filling changes the answer (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | Two reasonable choices, two answers | challenge | code | the learning outcome. `two_ways(df)` → mean income by city under (a) complete cases and (b) median fill within age band; returns both tables and the largest difference; on the test data the two answers differ by more than a stated amount, and each matches a slow computation |
| 31 | Mean filling shrinks the spread | drill | code | `fill_with_mean(s)` → `(filled, sd_before, sd_after)`; `sd_after < sd_before` whenever something was filled; nothing missing → identical |
| 32 | Drop, fill with the mean, fill with zero | applied | trace | `assessment = "trace"`. `⚠ HAND-TRACE` count, mean and sd (2 decimals) of 8 values with 3 NA under `dropna`, `fillna(mean)`, `fillna(0)` |
| 33 | Which rule when? | applied | explain | Ch. 9.7 table in your own words for four cases (a sensor gap of one hour, unanswered income question, a product never sold, a test score of an absent student); checklist: "mechanism", "what the gap means", "report both", "never fill a target", "zero only when zero is true" |

## I. Validation (Ch. 10–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 34 | Validation by hand | applied | code | `validate_table(df, rules)` (Ch. 10.1): each rule a name and a function returning a boolean Series; result is a list of `(rule, n_failed, first_ids)`; passing table → `[]` |
| 35 | A pandera schema | applied | code | `SCHEMA` (a module-level `pa.DataFrameSchema`) for the survey columns stated in `problem.md`; the test validates one good frame and five bad frames, each bad frame must fail on the stated column |
| 36 | Rules across columns | deep | code | `SCHEMA` with frame-level checks (`last_seen >= signup`, `student` implies `age < 30`); the failing rows' indexes are the stated ones (read from `failure_cases`) |
| 37 | Quarantine instead of crashing | deep | code | `split_valid(df, schema)` → `(valid, quarantine)`; quarantine rows carry a `reasons` column built from lazy `failure_cases`; valid + quarantine = all rows; schema-level failures (missing column) still raise |
| 38 | What does lazy validation report? | deep | trace | `⚠ HAND-TRACE` the `(column, check)` pairs of the measured example in Testing notes for a different 4-row frame; print sorted pairs |

## J. A pipeline you can trust, and the project (Ch. 12–13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 39 | Fix the pipeline that changes on every run | deep | code | `assessment = "fix"`. Given `clean(df, log)` that converts grams to kg **in place** each run, appends to a module-level log, and fills NA in the caller's frame; tests: running twice gives identical output (idempotence, Ch. 12.4), the input frame is unchanged, the log is only the passed one |
| 40 | A documented cleaning pipeline | challenge | code | `assessment = "build"` (project, Ch. 13). `clean_air(raw)` → `(clean, flags, log, report)` for an air-quality table made by a copy of `make_air` in `conftest.py`: formats, duplicates, suspects (spike, stuck sensor, impossible), schema + quarantine, and a missing-data section with both answers; the test checks known injected problems are all caught and the report names both answers |

## Counts check

Tiers: drill 1, 3, 4, 6, 8, 9, 11, 15, 19, 21, 24, 25, 31 = 13 ·
applied 2, 5, 7, 10, 12, 16, 20, 22, 23, 26, 32, 33, 34, 35 = 14 ·
deep 13, 14, 17, 27, 28, 29, 36, 37, 38, 39 = 10 · challenge 18, 30, 40 = 3. Total 40.
Kinds: trace 9, 13, 19, 25, 32, 38 = 6 · explain 3, 23, 28, 33 = 4 · code 30.
Assessments: explain p028, trace p032, fix p039, build p040.

## Risks and open questions

- p014: the "hanging" starter must not hang the validator forever: the test's subprocess limit protects it, but the
  starter given to the learner should be a stub (`return False`), not the bad regex. Put the bad regex in `problem.md`.
- p029/p030 margins: pick the effect sizes in the generator so the gap is several standard errors wide; verify 3 seeds.
- pandera changes its failure-case text between versions; tests compare **column names** and row indexes, never the
  `check` text, except in p038 whose expected output must be re-run when pandera is upgraded (say so in `solution.md`).
- p040 is long; keep the generated table to about 45 days × 3 stations so the test stays fast.
