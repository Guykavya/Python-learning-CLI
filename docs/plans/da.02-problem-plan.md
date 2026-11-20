# Problem plan: da.02 NumPy (50 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.02.p001` … `p050`, folder `pNNN-slug`.

**Mix:** 18 drill, 17 applied, 11 deep, 4 challenge. **Kinds:** 36 code, 9 trace, 5 explain.
**assessment:** explain = p035, trace = p030, fix = p015, build = p050.
**★ core set (write first, 20):** p001, p004, p007, p009, p014, p015, p019, p020, p021, p023, p025, p030, p031, p032, p033, p034, p036, p038, p042, p050.

**Testing notes**

- NumPy only (plus the standard library). Arrays are passed in by the test and returned (R1). Compare with
  `np.testing.assert_array_equal` / `assert_allclose(rtol=1e-12)`; check **dtype and shape** too, with their own
  messages ("your result is float64; the image must stay uint8").
- "No loops" problems: the test does not inspect source code. It uses an input big enough (10**6 elements) that a
  Python loop exceeds a time budget measured in a subprocess (as in dsa.11/dsa.12), with the message "looks like a
  Python loop: vectorise it (Ch. 12.1)". Keep the reference under 0.5 s.
- Random data in tests: `np.random.default_rng(seed)`, expected values computed from a slow loop version or a NumPy
  function, never hard-coded (R3: `Generator` streams are not promised stable across NumPy versions).
- Traces print `.tolist()`, `.shape`, `str(dtype)`, `int()`/`float()` only (NumPy 2 prints scalars as `np.float64(1.5)`).
- Measured on NumPy 2.5.4 (2026-11-18), usable in traces: `uint8 [200, 250] + 100` → `[44, 94]` uint8 (silent wrap);
  `uint8 + 300` → `OverflowError` (NEP 50); `uint8 + np.int64(100)` → int64; `uint8 + 2.5` → float64;
  `float32 + 1.5` → float32; slicing gives a view, fancy indexing a copy, `reshape` a view; `i[[0,0,1]] += 1` on zeros
  → `[1, 1, 0]` while `np.add.at` counts duplicates; `np.broadcast_shapes((5,1,4),(3,1))` → `(5, 3, 4)`;
  `np.percentile([15,20,35,40,50], 25)` → `20.0`.
- Memory: p037 relies on the 1 GiB cap (an unchunked 20,000 × 20,000 float64 matrix needs 3.2 GB → `MemoryError`).
  Run the reference under `ulimit -v 1000000` to be sure it fits.

## A. Why NumPy, creating arrays, anatomy (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Sum of squares without a loop | drill | code | `sum_squares(n)` = 0² + … + (n−1)²; n = 0, 1, 10, 10**6 (int64 is enough; message if a float is returned); time budget for 10**6 |
| 2 | Coordinates of a grid | drill | code | `grid_coordinates(h, w)` → `(ys, xs)` both shape `(h, w)` like `np.indices`; h or w = 0; dtype integer |
| 3 | Shape, size, dtype, strides | deep | trace | `⚠ HAND-TRACE` for 4 arrays with explicit `dtype=np.int64` (a 2×3, its transpose, a 2×3×4, a `[::2]` slice): print `shape`, `ndim`, `size`, `strides` |
| 4 | Which axis is which? | drill | code | `column_means(a)`, `row_maxes(a)`, `per_image_mean(stack)` for shape `(n, h, w)`; test on non-square arrays so a swapped axis fails with a shape message |
| 5 | Why is the array faster than the list? | drill | explain | Ch. 1.1–1.2; checklist: "pointers to objects", "one type", "one contiguous block", "loop runs in C", "no per-element type checks" |

## B. dtypes (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Overflow and promotion | deep | trace | `⚠ HAND-TRACE` the uint8 wrap and NEP 50 results listed in Testing notes (5 lines; one raises: print the exception class name via `try/except`) |
| 7 | Brighten an image safely | applied | code | `add_clipped(img, delta)` for a uint8 image: widen, add, `clip(0, 255)`, back to uint8; negative delta; dtype stays uint8; message "values wrapped round: 250 + 10 gave 4" |
| 8 | Comparing floats | drill | code | `close_mask(a, b, rtol, atol)` without `==`; `0.1 + 0.2` vs `0.3`; arrays with `nan` → False at those places |
| 9 | Mean that ignores nan and inf | drill | code | `clean_mean(x)` → `(mean, n_dropped)`; all bad → `(nan, n)` without a RuntimeWarning (test turns warnings into errors) |
| 10 | Truncation and rounding | deep | trace | `⚠ HAND-TRACE` `astype(int)` on `[2.5, 3.5, -1.7, 1e10]` (int64), and `np.round` on `[0.5, 1.5, 2.5]` (half to even); `.tolist()` output |

## C. Reshaping, joining, views and copies (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | Reshape into rows | drill | code | `to_rows(x, k)` with `-1`; not divisible → `ValueError` whose message names `len(x)` and `k`; result shares memory (`np.shares_memory`) |
| 12 | Stack or concatenate? | drill | trace | `⚠ HAND-TRACE` shapes from `concatenate`, `stack(axis=0)`, `stack(axis=1)`, `vstack`, `hstack`, `column_stack` of two length-3 vectors and of two 2×3 arrays |
| 13 | Split into batches | applied | code | `batches(x, size)` → list of arrays, last may be shorter; `size` larger than `len(x)`; `size <= 0` → `ValueError`; batches are views |
| 14 | View or copy? | applied | trace | `⚠ HAND-TRACE` the view/copy sequence of Testing notes (slice, fancy index, reshape, boolean mask) printing the original after each write |
| 15 | Fix the normaliser that edits your data | deep | code | `assessment = "fix"`. Given `normalise(x)` that does `x -= x.min(); x /= x.max()` (Ch. 6.3): it changes the caller's array and crashes on integer input (`UFuncTypeError`). Tests: caller unchanged, int input works, result float in `[0, 1]`, constant array → zeros |
| 16 | The huge array that will not go away | deep | explain | Ch. 6.4: a small slice keeps a 1 GB array alive; explain why and the fix (`.copy()`); checklist: "view", "base", "reference keeps memory", "copy the small part" |

## D. Indexing, masks and fancy indexing (Ch. 7–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Border and inside | drill | code | `border_values(a)` (clockwise from top-left, no repeated corners) and `interior(a)`; 1×1, 2×2, 1×n edge cases |
| 18 | An integer removes an axis | drill | trace | `⚠ HAND-TRACE` shapes of `a[1]`, `a[1:2]`, `a[:, 1]`, `a[:, [1]]`, `a[..., 0]`, `a[None]` for `a` of shape `(3, 4, 5)` |
| 19 | Filter rows with several conditions | drill | code | `select_rows(table, col, lo, hi, exclude=None)` with `&`, `|`, `~` in brackets; empty result has shape `(0, ncols)`; message on the precedence trap of Ch. 8.2 |
| 20 | Grades with `np.select` | applied | code | `grades(scores)` → array of `"A"…"F"` with boundaries in `problem.md`; boundary values; `nan` → `"missing"` |
| 21 | Replace outliers with the median | applied | code | `cap_outliers(x, k=1.5)` sets values outside the IQR fences to the median (da.01 revisited, Ch. 8.5); returns a new array; the count replaced as second value |
| 22 | Pick pairs | applied | code | `pick(matrix, rows, cols)` with two index arrays; `diagonal_of_top(matrix, k)`; out-of-range index → `IndexError` passes through |
| 23 | The duplicate-index trap | deep | code | `count_by_index(idx, n)` and `add_amounts(totals, idx, amounts)` with duplicate positions; `x[idx] += 1` gives the wrong count (message quotes the measured `[1, 1, 0]`); must use `np.add.at` or `bincount` |
| 24 | Ranks from `argsort` | drill | code | `ranks(x)` 0-based, ties broken by position (stated); descending option; compared with a sorted-loop version |

## E. ufuncs and aggregations (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Row shares with `keepdims` | drill | code | `row_shares(x)` each row sums to 1; an all-zero row → zeros, not `nan` (no RuntimeWarning) |
| 26 | Running balance | applied | code | `running_balance(opening, txns)` with `cumsum`; `first_overdraft_day(...)` → index or `-1`; empty txns |
| 27 | Per-column stats with gaps | deep | code | `column_stats(x)` → dict of `mean`, `std`, `count` per column with `nan`s; an all-`nan` column gives `nan` mean and count 0 with **no** RuntimeWarning (warnings as errors) |
| 28 | Tables with `outer` | drill | code | `times_table(n)` and `pairwise_diff(a, b)` with `np.multiply.outer` / `np.subtract.outer`; shapes `(len(a), len(b))` |
| 29 | What type does a sum have? | applied | trace | `⚠ HAND-TRACE` `sum` of a bool array, `mean` of an int array, `sum(dtype=np.uint8)` overflow on `[200, 100]`, `np.cumsum` of uint8 → printed with `int()`/`str(dtype)` (verify each line by running) |

## F. Broadcasting and vectorisation (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | Predict the broadcast shape | deep | trace | `assessment = "trace"` (learning outcome). `⚠ HAND-TRACE` 8 pairs of shapes: result shape or `error`; e.g. `(3,1)+(4,)`, `(5,1,4)+(3,1)`, `(2,3)+(3,2)`, `(8,1,6,1)+(7,1,5)`; check with `np.broadcast_shapes` |
| 31 | Broadcasting rules by hand | challenge | code | `broadcast_shape(*shapes)` without NumPy's helper; compared with `np.broadcast_shapes` on 200 random shape pairs; incompatible → `ValueError` naming the axis |
| 32 | Standardise each column | applied | code | `zscore(x, axis=0, ddof=0)`; constant column → 0; `axis=1` too; matches the chapter's `nptools.zscore` behaviour |
| 33 | Pairwise distances | deep | code | `pairwise_distances(a, b)` `(n,d)`,`(m,d)` → `(n,m)` Euclidean with broadcasting; compared with a loop on small data; 2,000 × 2,000 × 3 within budget |
| 34 | Replace the loops | challenge | code | three loop functions given (piecewise tax, clipped day-to-day change, nearest centre); write `tax_vec`, `change_vec`, `nearest_vec`; equal to the loops on random data; 10**6 input within the time budget |
| 35 | `np.vectorize` is not a speed-up | deep | explain | `assessment = "explain"`. Ch. 12.3: explain why `np.vectorize` runs at Python speed and what to use instead; checklist: "Python function per element", "convenience", "ufuncs", "where/select", "measure" |
| 36 | Moving average with `cumsum` | applied | code | `moving_average(x, k)` (length `n-k+1`); compared with `np.convolve(x, ones(k)/k, "valid")`; `k > n` or `k < 1` → `ValueError` |
| 37 | Nearest neighbour in chunks | challenge | code | `nearest_distance(points, chunk=250)` for 20,000 points: the full matrix does not fit under the 1 GiB cap, chunks do; compared with a small brute force on 500 points |

## G. Random numbers (Ch. 13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 38 | Dice with a Generator | drill | code | `simulate_rolls(n, rng)` → counts for faces 1–6; uses the **passed** `rng` (two generators with the same seed give the same counts; message about `np.random.seed`/global state) |
| 39 | Sample without replacement | applied | code | `sample_rows(x, k, rng)`; no repeats; `k > len(x)` → `ValueError`; input not shuffled in place |
| 40 | One seed, many streams | applied | explain | Ch. 13.5: why `default_rng(seed + i)` per worker is worse than `SeedSequence(seed).spawn(n)`; checklist: "independent streams", "reproducible", "spawn", "do not reuse a generator across workers" |
| 41 | The law of large numbers | drill | code | `running_mean_of_flips(n, rng)` → array of running means; length `n`; last value within 0.02 of 0.5 for n = 10**5 on 3 seeds; first value is 0 or 1 |

## H. Statistics, sorting, unique and sets (Ch. 14–15)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 42 | da.01 percentiles in NumPy | drill | code | `percentile(x, p, method)` mapping the da.01 names (`"inclusive"`, `"exclusive"`, `"nearest_rank"`) to NumPy `method=` values; checked against `statistics.quantiles` and the da.01 definitions |
| 43 | Which bin does it fall in? | applied | trace | `⚠ HAND-TRACE` `np.digitize` with `right=False` and `right=True`, and `searchsorted` left/right, for values on the bin edges |
| 44 | Sort by several keys | applied | code | `sort_records(names, scores, ages)` → order: score desc, age asc, name asc, via `np.lexsort` (last key first); compared with Python `sorted` |
| 45 | New and lost customers | drill | code | `customer_changes(jan_ids, feb_ids)` → `(new, lost, kept)` sorted arrays with `setdiff1d`/`intersect1d`; duplicates in input; empty months |
| 46 | Top k without a full sort | applied | code | `top_k(x, k)` with `argpartition`, result sorted descending; `k = 0`, `k >= n`; time budget on 10**6 |

## I. Linear algebra, saving (Ch. 16, 18)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 47 | Fit a line with `lstsq` | applied | code | `fit_line(x, y)` → `(slope, intercept)`; compared with `np.polyfit(x, y, 1)`; vertical data (all `x` equal) → `ValueError` |
| 48 | Why not `inv`? | deep | explain | Ch. 16.3–16.4: why `solve` beats `inv(A) @ b`, and what a near-singular matrix does; checklist: "slower", "less accurate", "condition number", "solve directly", "check the residual" |
| 49 | Save and load a dataset | applied | code | `save_dataset(path, **arrays)` and `load_dataset(path)` with `.npz`; round trip keeps dtypes and names; path from `tmp_path`; `allow_pickle` stays False (object array → clear `ValueError`) |

## J. Project (Ch. 19–20)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 50 | Image pipeline | challenge | code | `assessment = "build"`. `to_gray`, `adjust(img, brightness, contrast)`, `flip`, `blur3`, `equalise`, `pipeline(img, steps)` on a synthetic RGB image built by the test (Ch. 20.2 style); dtype stays uint8, shapes kept, `blur3` equals a loop version on a 6×6 image, `equalise` output uses the full 0–255 range, `pipeline([])` returns a copy |

## Counts check

Tiers: drill 1, 2, 4, 5, 8, 9, 11, 12, 17, 18, 19, 24, 25, 28, 38, 41, 42, 45 = 18 ·
applied 7, 13, 14, 20, 21, 22, 26, 29, 32, 36, 39, 40, 43, 44, 46, 47, 49 = 17 ·
deep 3, 6, 10, 15, 16, 23, 27, 30, 33, 35, 48 = 11 · challenge 31, 34, 37, 50 = 4. Total 50.
Kinds: trace 3, 6, 10, 12, 14, 18, 29, 30, 43 = 9 · explain 5, 16, 35, 40, 48 = 5 · code 36.
Assessments: explain p035, trace p030, fix p015, build p050.

## Risks and open questions

- Time-budget tests are machine-dependent: set the budget at about 10× the reference time on this laptop and check
  that a plain loop takes at least 5× the budget, so slow Windows machines do not fail correct answers.
- p027/p009 "no RuntimeWarning" tests: `np.nanmean` of an all-`nan` slice warns; the learner must handle it. Use
  `warnings.catch_warnings(); simplefilter("error")` only around the call under test.
- p037 depends on the runner's memory cap, which does **not** exist on Windows. Give it a second check that works
  everywhere (a monkeypatched `chunk` size is respected: the test counts calls of a helper, or checks peak array size).
- p029 and p006: run every printed line once before writing `expected.txt`; NumPy 2.x promotion rules are easy to misremember.
