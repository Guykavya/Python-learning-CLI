# Problem plan: da.03 pandas core (60 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.03.p001` … `p060`, folder `pNNN-slug`.

**Mix:** 21 drill, 22 applied, 12 deep, 5 challenge. **Kinds:** 46 code, 10 trace, 4 explain.
**assessment:** explain = p049, trace = p024, fix = p025, build = p060.
**★ core set (write first, 24):** p001, p003, p006, p009, p011, p017, p019, p023, p024, p025, p028, p030, p033, p035, p036, p038, p044, p045, p048, p050, p053, p055, p056, p060.

**Testing notes**

- Frames are built **inline in the test** (5–15 rows the author can check by eye) or by a small generator in
  `conftest.py` modelled on the chapter's `make_orders` / `make_messy_sales` (Ch. 5.1, 19.1). Expected values for
  generated data are computed in the test with an obvious pandas or plain-Python version, never hard-coded (R3).
- I/O problems (Ch. 6): the **test writes** the CSV/JSON/Excel/Parquet/SQLite file into `tmp_path` and passes the
  path; output files go to a path the test passes in (R1). Excel via openpyxl, Parquet via pyarrow (both installed).
  SQL problems get an open `sqlite3` connection from the test.
- Compare frames with `pd.testing.assert_frame_equal(check_dtype=…)`; say in each message which column or dtype differs.
  Always check the **input frame is unchanged** where the statement promises it (keep `df.copy()` and compare).
- Copy-on-Write: pandas **3.1.1** is installed. Measured 2026-11-18: chained assignment `df[df.a > 1]["b"] = 0` changes
  nothing and emits `ChainedAssignmentError` (a warning); `s = df["a"]; s.iloc[0] = 99` leaves `df` unchanged; but a
  plain alias `y = x; y.iloc[0] = 9` does change `x`. The chapter teaches pandas 3 (Ch. 9.2–9.3); problems follow it.
- Other measured facts usable in traces: `Series([10,20,30], index=[2,0,1])[0]` → `20` (label) and `.iloc[0]` → `10`;
  `a + b` with partly different labels → `[nan, 12.0, 23.0, nan]`; `df.loc[10:20]` includes 20; text dtype prints as
  `str` (pandas 3), `[1, None]` → `float64`, `[True, None]` → `object`; `Series([nan]).sum()` → `0.0`;
  `pd.to_datetime` on `["01/02/2024", "13/02/2024"]` raises `ValueError` (mixed day/month order);
  `rank()` of `[3,1,3,2]` → `[3.5, 1.0, 3.5, 2.0]`, `method="dense"` → `[3.0, 1.0, 3.0, 2.0]`.
- Traces never print a DataFrame or Series repr (R3): they print `.tolist()`, `.shape`, `str(dtype)`, `type(x).__name__`.
- Time budgets ("no `iterrows`") as in da.02: measured in a subprocess on 200,000 rows, budget about 10× the reference.

## A. Series, DataFrame and the index (Ch. 1–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Label or position? | drill | code | `price_of(s, label)` and `nth_price(s, n)` on a Series whose integer index is **not** `0..n-1`; message "you used `s[n]`, which is a label lookup" |
| 2 | Predict label versus position | drill | trace | `⚠ HAND-TRACE` `s[0]`, `s.iloc[0]`, `s.loc[1]`, `s.iloc[-1]` for `Series([10,20,30], index=[2,0,1])`, and one `KeyError` caught and printed by name |
| 3 | Add two months that do not match | drill | code | `combine_months(a, b)` aligned by product; a product in only one month counts as 0 (`add(fill_value=0)`); result sorted by label; integer dtype kept |
| 4 | Predict alignment | applied | trace | `⚠ HAND-TRACE` the measured `a + b` alignment, then `a.add(b, fill_value=0)`, then `a.values + b.values` (position-wise), printed with `.tolist()` |
| 5 | A table from records | drill | code | `orders_frame(records)` from a list of dicts: fixed column order, `order_date` parsed, `qty` int; missing keys become missing values |
| 6 | Choose the index, and check it | applied | code | `index_by(df, key)` sets the index and raises `ValueError` listing the duplicated keys if it is not unique (Ch. 4.2) |
| 7 | Old labels stay after a filter | drill | trace | `⚠ HAND-TRACE` filter a frame, then `.loc[0]` (KeyError), `.iloc[0]`, `reset_index(drop=True).loc[0]`; print values |
| 8 | A small MultiIndex | applied | code | `sales_for(df, region, month)` via `set_index(["region","month"])`; a missing combination → 0, not `KeyError`; `sales_by_region(df)` sums over the inner level |

## B. First look and files (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | The first five questions | drill | code | `first_look(df)` → dict: `rows`, `cols`, `dtypes` (as strings), `missing` per column, `duplicate_rows`; checked against direct pandas calls |
| 10 | Count values, including gaps | drill | code | `category_counts(s)` with `dropna=False`, plus shares; missing shown as `"(missing)"` label; order by count then label |
| 11 | Read a European-style CSV | applied | code | `read_shop_csv(path)` for `;` separator, `,` decimals, `.` thousands, `-` as missing, a date column; the test checks dtypes and two values, messages name the `read_csv` parameter |
| 12 | Keep the leading zeros | drill | code | `read_with_codes(path)` keeps `pin` and `product_code` as text (`dtype=`); `"007"` stays `"007"` |
| 13 | Nested JSON to a table | deep | code | `orders_from_json(records)` with `pd.json_normalize`: one row per order line (`record_path`), order fields repeated (`meta`); missing nested key → missing value |
| 14 | Read from SQL with parameters | applied | code | `orders_since(con, since)` uses `read_sql_query(..., params=)`; a value with a quote in it works (no f-string SQL); dates parsed |
| 15 | Which file format when? | applied | explain | five situations (hand to a manager, keep types for the next script, 50 M rows, nested API data, a database already exists); checklist: "CSV loses types", "Parquet keeps types and is columnar", "Excel for people", "JSON for nesting", "query in the database" |
| 16 | An Excel report with several sheets | applied | code | `write_report(path, sheets)` writes each frame to its own sheet without the index; the test reads back with `read_excel(sheet_name=None)` and compares |

## C. Selecting and filtering (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Inclusive or exclusive slice? | drill | trace | `⚠ HAND-TRACE` shapes and first/last labels of `loc["b":"d"]`, `iloc[1:3]`, `loc[:, "x":"z"]`, `iloc[:, 1:]` on a small labelled frame |
| 18 | What does a bare `[]` give? | drill | trace | `⚠ HAND-TRACE` `type(...).__name__` and `.shape` of `df["a"]`, `df[["a"]]`, `df[1:3]`, `df[df.a > 1]` (Ch. 7.5) |
| 19 | Filter with brackets | drill | code | `big_orders(df, city, min_amount)` with `&`, `|`, `~`; the precedence trap (`df.a > 1 & df.b < 2`) gets its own failing case and message |
| 20 | `isin`, `between` and `.str.contains` | applied | code | `filter_products(df, categories, lo, hi, word)`; `between` is inclusive; case-insensitive word match; missing names do not crash (`na=False`) |
| 21 | Filters as text with `query` | applied | code | `query_orders(df, min_qty, region)` using `@` variables and a column with a space (backticks) |
| 22 | `where`, `mask` and `pd.col` | applied | code | `cap_discounts(df, cap)` keeps the shape; discount above the cap set to the cap; uses `where`/`mask` or `pd.col` (Ch. 8.5), result equal to a loop version |

## D. Changing values safely (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | Change values with `loc` | drill | code | `apply_discount(df, category, pct)` returns a new frame; only matching rows change; the input is unchanged |
| 24 | Chained assignment in pandas 3 | deep | trace | `assessment = "trace"`. `⚠ HAND-TRACE` the measured Copy-on-Write sequence: chained assignment (nothing changes; print the warning class name caught with `warnings.catch_warnings(record=True)`), `s = df["a"]` edit, `.loc` edit, plain alias edit |
| 25 | Fix the cleaning function that does nothing | deep | code | `assessment = "fix"`. Given `clean(df)` using `df[df.qty < 0]["qty"] = 0` and `df["price"][i] = ...` in a loop; tests: values really change, **no** `ChainedAssignmentError` (warnings as errors), the input frame is unchanged |
| 26 | Assigning a Series with other labels | deep | code | `attach_targets(df, targets)` where `targets` is indexed by `customer_id` and `df` by position: plain assignment gives NaN (alignment); the solution maps by key; missing keys stay NA and are counted |

## E. dtypes and missing data (Ch. 10–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Integers with gaps | drill | code | `to_nullable_ints(df, cols)` → `Int64`; values with `.0` are fine, `2.5` → `ValueError` naming the column |
| 28 | Convert, and count what was lost | applied | code | `convert_numbers(s)` → `(numbers, bad_values)` with `to_numeric(errors="coerce")`; `bad_values` lists raw texts that were not empty but became NA |
| 29 | Categories that save memory | deep | code | `as_category(df, max_unique=50)` converts low-cardinality text columns; values equal; `memory_usage(deep=True)` smaller; high-cardinality columns untouched |
| 30 | Missing values in sums and means | deep | trace | `⚠ HAND-TRACE` `sum`, `mean`, `count`, `sum(min_count=1)` on `[1, nan, 3]` and on `[nan]`, `nan == nan`, `isna()`; floats printed with `float()` |
| 31 | Fill, interpolate or drop | applied | code | `fill_gaps(s, how)` for `"drop"`, `"zero"`, `"ffill"`, `"interpolate"`, `"median"`; leading NA with `ffill` stays NA (stated); unknown `how` → `ValueError` |
| 32 | Why did my integers become floats? | drill | explain | Ch. 10.2: explain why `[1, None, 3]` is `float64` and what `Int64` changes; checklist: "NaN is a float", "nullable dtype", "pd.NA", "convert after cleaning" |

## F. Text and dates (Ch. 12–13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 33 | Tidy a name column | drill | code | `tidy_names(s)`: strip, collapse inner spaces, title case; missing stays missing; non-ASCII names kept |
| 34 | Split into two columns | applied | code | `split_full_name(df)` → `first`, `last` with `str.split(n=1, expand=True)`; one-word names → empty last name (stated) |
| 35 | Money stored as text | applied | code | `to_money(s)` with the rules of Ch. 12.4 / 18.2 (currency sign, commas, spaces, `"-"` → NA); a table of 12 cases |
| 36 | Dates in three formats | challenge | code | `parse_dates(s, formats)` tries each format in order (`format=` per attempt, `errors="coerce"`), returns parsed dates and the unparsed raw values; ambiguous `01/02/2024` follows the stated format order |
| 37 | Date parts | drill | code | `add_date_parts(df, col)` → `year`, `month`, `quarter`, `weekday` (name), `is_weekend` |
| 38 | Delivery times | applied | code | `delivery_report(df)` → `days` (timedelta in days, float), `late` flag (> promised days); undelivered orders: NA days, not late |
| 39 | Periods and month ends | applied | trace | `⚠ HAND-TRACE` `to_period("M")` as strings, `Timestamp("2024-01-31") + DateOffset(months=1)`, `+ MonthEnd(1)`, `dt.days_in_month` for Feb 2024; run to confirm |
| 40 | Day first or month first? | drill | explain | Ch. 13.2: why `03/04/2024` is dangerous, what pandas does with mixed rows (raises), how to decide; checklist: "ambiguous", "state the format", "dayfirst", "check impossible days like 13", "count failures" |

## G. Columns and rows (Ch. 14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 41 | Rename, drop, assign | drill | code | `prepare(df)` in one chain: snake_case names, drop helper columns, add `revenue = qty * price`; input unchanged |
| 42 | Sort by several keys | applied | code | `rank_sellers(df)`: revenue desc, then name asc, missing revenue last; ties stable |
| 43 | Four kinds of rank | drill | trace | `⚠ HAND-TRACE` `rank()` with `average`, `min`, `dense`, `first` on `[3, 1, 3, 2]` (measured values in Testing notes) |
| 44 | Keep the latest row per customer | applied | code | `latest_per_customer(df)` with `sort_values` + `drop_duplicates(keep="last")`; ties on time broken by `row_id`; count of removed rows returned |

## H. Vectorised versus `apply`, bins (Ch. 15)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 45 | Replace `iterrows` | deep | code | given a loop that computes line totals with a tiered discount, write `line_totals(df)` without loops; equal on random data; time budget on 200,000 rows |
| 46 | Map codes to names | drill | code | `map_regions(s, mapping)` → mapped Series with unknown codes as `"Other"`, plus the sorted list of unknown codes |
| 47 | A priority column with `np.select` | drill | code | `priority(df)` with three ordered conditions (first match wins) and a default |
| 48 | Equal widths or equal counts? | applied | code | `age_bands(s)` with `cut` (edges and right-closed rule stated) and `spend_quartiles(s)` with `qcut`; labels; boundary values land in the stated band |
| 49 | When is `apply` the right answer? | deep | explain | `assessment = "explain"`. Ch. 15.1–15.5: compare vectorised, `map` and `apply`, and name a case where `apply` is right; checklist: "row-wise Python call", "slow on big data", "vectorised first", "apply for complex per-group/per-row logic", "measure" |

## I. Summaries (Ch. 16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 50 | Average price, weighted | applied | code | `summary_numbers(df)` → revenue, orders, units, **weighted** average price `sum(q*p)/sum(q)`; the unweighted mean gets its own failing case and message |
| 51 | Daily changes | applied | code | `daily_changes(s)` → `diff`, `pct_change`, running total; first row NA; zero yesterday → `inf` replaced by NA (stated) |
| 52 | Describe one column | applied | code | `describe_column(s)` → dict like da.01 `describe` (n, missing, mean, median, sd, q1, q3, skew) using pandas; equal to the da.01 numbers on the same data |

## J. Chains, toolkit and project (Ch. 17–19)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 53 | One recipe instead of six variables | deep | code | rewrite a given script with temporaries into `clean_orders(df)` as one method chain (`assign`, `query`, `pipe`); output equal to the script's; input unchanged |
| 54 | Shrink a frame | deep | code | `shrink(df)` downcasts numbers and makes categories; every value equal; memory ≤ 50% of the original on the generated data |
| 55 | `profile`: one screen per table | challenge | code | `profile(df, top=3)` → one row per column: dtype, missing, unique, top values with counts, min/max for numbers; checked column by column against direct pandas calls |
| 56 | `load_sales`: text first, then convert | challenge | code | `load_sales(path, money=…, dates=…, bools=…, ints=…)` reads everything as text, converts each group with the da.03 helpers, returns `(df, losses)` where `losses` counts values lost per column; CSV written by the test |
| 57 | Where did the values go? | deep | code | `conversion_losses(raw, clean)` → per column, how many non-empty raw values became NA, with up to 3 examples; the problem register of Ch. 19.5 |
| 58 | Six business questions | challenge | code | functions for revenue by month, top 5 products, channel share, average order value, repeat-customer share, returns rate on a cleaned frame; each checked against a slow plain-Python computation in the test |
| 59 | Count the rows through a pipeline | deep | trace | `⚠ HAND-TRACE` a 10-row frame through `dropna(subset=…)`, `drop_duplicates()`, a filter and `drop_duplicates(subset=…, keep="last")`; print the row count after each step |
| 60 | Explore a messy sales file | challenge | code | `assessment = "build"` (project). `explore(path, out_dir)` loads with `load_sales`, writes `clean.parquet` and `problems.csv` (register) into `out_dir`, returns the six answers as a dict; the test makes the messy file with a copy of the chapter's `make_messy_sales` in `conftest.py` and checks answers against its own slow computation |

## Counts check

Tiers: drill 1, 2, 3, 5, 7, 9, 10, 12, 17, 18, 19, 23, 27, 32, 33, 37, 40, 41, 43, 46, 47 = 21 ·
applied 4, 6, 8, 11, 14, 15, 16, 20, 21, 22, 28, 31, 34, 35, 38, 39, 42, 44, 48, 50, 51, 52 = 22 ·
deep 13, 24, 25, 26, 29, 30, 45, 49, 53, 54, 57, 59 = 12 · challenge 36, 55, 56, 58, 60 = 5. Total 60.
Kinds: trace 2, 4, 7, 17, 18, 24, 30, 39, 43, 59 = 10 · explain 15, 32, 40, 49 = 4 · code 46.
Assessments: explain p049, trace p024, fix p025, build p060.

## Risks and open questions

- pandas 3 is new: behaviour differs from almost every tutorial a free chatbot learned from (CoW, `str` dtype,
  removed chained assignment). When a chatbot writes these problems, **run every trace line** and check every
  "this warns / this raises" claim against the installed version before shipping.
- p039: offset aliases have changed across pandas versions (`"M"` → `"ME"`); use `DateOffset`/`MonthEnd` objects,
  not alias strings, so the trace survives future versions.
- p016: `read_excel` needs openpyxl; writing many small sheets is slow-ish (~0.5 s), fine within budget.
- p060 depends on p056 and the chapter's generator; copy the generator into `conftest.py` exactly (Ch. 19.1) and keep
  the file at ≤ 1,200 rows so the test stays under 20 s.
