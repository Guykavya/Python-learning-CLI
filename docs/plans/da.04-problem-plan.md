# Problem plan: da.04 pandas transformations (60 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.04.p001` … `p060`, folder `pNNN-slug`.

**Mix:** 20 drill, 23 applied, 12 deep, 5 challenge. **Kinds:** 48 code, 8 trace, 4 explain.
**assessment:** explain = p030, trace = p020, fix = p026, build = p060.
**★ core set (write first, 24):** p001, p003, p005, p007, p008, p009, p014, p015, p017, p020, p021, p022, p025, p026, p030, p031, p035, p036, p037, p038, p044, p046, p057, p060.

**Testing notes**

- The chapter's retail world (`make_retail`, Ch. 1.1: customers, products, stores, orders, items, returns) is
  the setting. Tests build **small inline versions** of these tables (4–12 rows each) so every expected number can be
  checked by hand; property tests use a small seeded generator in `conftest.py` and compare with a slow
  plain-Python computation (dicts and loops) written in the test (R3).
- Frames in, frames out (R1). Compare with `pd.testing.assert_frame_equal` after `sort_values(...).reset_index(drop=True)`
  unless order is the point; check the input frames are unchanged.
- Every merge problem also checks the **row count** (the chapter's golden rule, Ch. 6.3) with its own message.
- Measured on pandas 3.1.1 / Polars 2.1.0 (2026-11-18): `groupby` drops missing keys by default (`dropna=False` keeps
  them); categorical `groupby` defaults to `observed=True` (unused categories vanish, no warning); `merge(validate="m:1")`
  with a duplicated right key raises `pandas.errors.MergeError`; a 2×2 many-to-many merge gives 4 rows;
  `rolling(2).mean()` on `[1,2,3,4]` → `[nan, 1.5, 2.5, 3.5]`, with `min_periods=1` → `[1.0, 1.5, 2.5, 3.5]`;
  `resample("ME")` works and `resample("M")` raises `ValueError`; Polars `group_by(..., maintain_order=True)` keeps
  first-seen order (without it the order is not defined, so tests sort).
- Polars problems receive a `pl.DataFrame`/`pl.LazyFrame` built by the test and are compared with the pandas answer
  through `.to_dicts()` after sorting. Under the 1 GiB cap pandas + Polars + DuckDB import fine **with the runner's
  environment** (`OMP_NUM_THREADS=2`, `MALLOC_ARENA_MAX=2`); without those variables the same imports failed with
  "failed to map segment" (measured), so each test file imports only the libraries it needs.
- Traces print `.tolist()`, `len()`, `.shape`, `list(df.columns)`; never a frame repr (R3).

## A. Split-apply-combine and `groupby` basics (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Revenue by one key or several | drill | code | `revenue_by(items, keys)` → flat frame (`as_index=False` or `reset_index`) sorted by the keys; one key and two keys |
| 2 | Where did the missing key go? | drill | trace | `⚠ HAND-TRACE` sums by a key with a `None`: default `groupby` (dropped) against `dropna=False`, and `size()` of each; print `.to_dict()`/`.tolist()` |
| 3 | `size`, `count` and `nunique` | drill | code | `customer_counts(orders)` → rows, orders with a coupon (non-missing count), distinct products per customer; the three columns get their own messages |
| 4 | What does iterating a groupby give? | drill | trace | `⚠ HAND-TRACE` `for key, part in df.groupby("k")`: print key and `len(part)` in order; then `get_group` and `ngroups` |

## B. Aggregation (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Named aggregation | drill | code | `store_summary(items)` with `agg(orders=("order_id", "nunique"), revenue=…, units=…)`; column names exact |
| 6 | Your own aggregation: p90 | applied | code | `p90_delivery_days(orders)` per region with a custom function (Ch. 3.3); groups of one value; compared with `quantile(0.9)` |
| 7 | Aggregate a computed value | applied | code | `net_revenue_by_category(items, products)`: compute `qty * price * (1 - discount)` **before** grouping; the "sum of prices times sum of quantities" mistake gets a failing case |
| 8 | Average order value done right | deep | code | `average_order_value(items)` overall and per store; the mean of store averages differs from the overall AOV on the test data (message explains the weights, Ch. 3.5) |

## C. `transform`, `filter`, `apply` (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Share of the group total | drill | code | `share_of_store(items)` adds a column with `transform("sum")`; shares in each store sum to 1; length equals the input |
| 10 | Fill gaps with the group median | applied | code | `fill_price_by_category(products)`; a category with no prices at all stays missing (stated) and is reported |
| 11 | Keep only busy customers | drill | code | `busy_customers(orders, min_orders)` with `filter`; returns all their rows; nobody qualifies → empty frame with the same columns |
| 12 | Same groups, three shapes | drill | trace | `⚠ HAND-TRACE` `len()` of `agg`, `transform` and `filter` results on one 8-row frame (Ch. 4) |
| 13 | `apply`: flexible, and when to avoid it | deep | explain | Ch. 4.3 and 12.2: what `apply` on groups costs and the three faster replacements; checklist: "Python call per group", "built-in aggregations are vectorised", "transform", "sort + head", "measure first" |

## D. Running values and top-N inside groups (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 14 | Running total per customer | drill | code | `running_spend(orders)` sorted by date inside customers, `cumsum`; input order shuffled by the test |
| 15 | Days since the previous order | applied | code | `days_between_orders(orders)` with `groupby().shift()`/`diff()`; first order NA; two orders on the same day → 0 |
| 16 | Month-on-month growth per store | applied | code | `store_growth(monthly)` with `pct_change` inside stores; a zero month → NA, not `inf` (stated) |
| 17 | Top 3 products per category | deep | code | `top_products(items, products, n=3)`; ties broken by product name (stated); a category with fewer than 3 products; result equals the slow per-category loop |
| 18 | Order number per customer | drill | code | `number_orders(orders)` → `order_no` starting at 1 via `cumcount`; `first_orders(orders)` keeps order 1 |
| 19 | Ranks inside groups | applied | trace | `⚠ HAND-TRACE` `groupby("store")["revenue"].rank(method="dense", ascending=False)` on 7 rows with a tie; print the list |

## E. `merge` (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | Four joins, four row counts | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` row counts of inner, left, right and outer merges of a 5-row and a 4-row table with one duplicate key, plus `_merge` value counts from `indicator=True` |
| 21 | Every order, with its customer | drill | code | `orders_with_customers(orders, customers)` left join; row count equals orders; orders with unknown customers kept with NA name and counted |
| 22 | Customers who never ordered | drill | code | `never_ordered(customers, orders)` anti-join (`indicator` or `~isin`); result has only customer columns |
| 23 | Customers who bought X (no duplicates) | applied | code | `bought_product(customers, items, product_id)` semi-join; a customer who bought it three times appears once |
| 24 | Different key names | applied | code | `attach_store_names(orders, stores)` with `left_on`/`right_on`, the duplicate key column dropped, clear `suffixes` |
| 25 | Let pandas check the relationship | applied | code | `lookup_products(items, products)` with `validate="m:1"`; duplicated product ids → `ValueError` whose message lists them (catch `MergeError` and re-raise clearly) |
| 26 | Fix the doubled revenue | deep | code | `assessment = "fix"`. Given `revenue_report(orders, payments)` that merges orders to **several** payments per order and then sums the order amount (fan-out, Ch. 6.8); tests: total equals the orders' own total, row count of the base table preserved, payment status still reported |
| 27 | Keys that refuse to match | deep | code | `normalise_keys(left, right, key)` fixes text vs integer ids, spaces and case (Ch. 6.9); returns cleaned frames and the match rate before/after; values that still fail are listed |
| 28 | Join on two columns | applied | code | `daily_targets(sales, targets)` on `(store_id, date)`; one-column merge gives a fan-out (failing case with message) |
| 29 | Every store, every month | applied | code | `full_grid(sales, stores, months)` with a cross join, then left join of sales, missing → 0; row count = stores × months |
| 30 | Count the rows before and after | deep | explain | `assessment = "explain"`. Ch. 6.3, 6.7, 6.8: explain how a merge can add, lose or duplicate rows and the three habits that catch it; checklist: "grain of each table", "row count before and after", "validate=", "indicator=True", "fan-out", "check a total" |

## F. `join`, `merge_asof`, `concat`, patches (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 31 | The price at the time of the order | applied | code | `price_at_order(orders, price_history)` with `merge_asof(by="product_id", direction="backward")`; inputs arrive unsorted; an order before the first price → NA |
| 32 | Stack monthly files | drill | code | `stack_months(frames: dict[str, DataFrame])` with `concat`, a `month` column from the dict key, `ignore_index=True`; a file with an extra column → NA elsewhere |
| 33 | Patch one table with another | applied | code | `patch_customers(old, fixes)` with `combine_first`/`update`; fixes win, missing fixes do not erase values |
| 34 | `concat` with mismatched columns | deep | trace | `⚠ HAND-TRACE` shape, `list(columns)` and NA count after `concat` of frames with different columns, with `join="inner"`, and with `axis=1` on different indexes |

## G. Reshaping: wide and long (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Long to wide | drill | code | `to_wide(monthly)` with `pivot` (store rows, month columns); duplicate (store, month) → `ValueError` with a message pointing to `pivot_table` |
| 36 | Pivot table with totals | applied | code | `region_month_table(items)` with `pivot_table(aggfunc="sum", fill_value=0, margins=True)`; totals row and column equal the grand total |
| 37 | Wide to long | drill | code | `to_long(wide)` with `melt(id_vars=…, var_name="month", value_name="sales")`; months stay in calendar order (stated) |
| 38 | There and back again | challenge | code | `to_wide`/`to_long` as exact inverses on random long data (missing combinations dropped on the way back); round trip compared after sorting; dtypes preserved |
| 39 | `stack` and `unstack` | deep | trace | `⚠ HAND-TRACE` shapes and `index.names` after `unstack()`, `unstack(0)`, `stack()` on a two-level series of 6 values |
| 40 | Counts of combinations | applied | code | `channel_by_region(orders)` with `crosstab`, raw and `normalize="index"` (rows sum to 1) |
| 41 | One row per tag | drill | code | `tag_counts(products)` splits a `"tags"` text column, `explode`s and counts; empty tags ignored |
| 42 | Categories to flags | drill | code | `channel_flags(orders)` with `get_dummies(prefix="ch", dtype=int)`; the flags in each row sum to 1 |
| 43 | Columns with a shared stem | challenge | code | `yearly_long(df)` turns `sales_2023, sales_2024, units_2023, units_2024` into rows per year with `wide_to_long` (or `melt` + split); checked against a loop version |

## H. Time series (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 44 | A full calendar | applied | code | `daily_sales(orders, start, end)` → one row per day with `reindex(date_range)`, missing days 0; the day count is checked |
| 45 | Weekly and monthly totals | applied | code | `period_totals(daily, freq)` for `"W-MON"` and `"ME"`; message if `"M"` is used ("pandas 3 removed this alias, Ch. 9.3") |
| 46 | Seven days or seven rows? | deep | code | `rolling_week(daily)` with a time-based window `"7D"` on data **with gaps**; differs from `rolling(7)` on the test data (failing case with message) |
| 47 | Monthly totals per store | applied | code | `store_month(orders)` with `groupby(["store_id", pd.Grouper(key="date", freq="ME")])`; equals a loop version |
| 48 | Rolling and `min_periods` | drill | trace | `⚠ HAND-TRACE` the measured `rolling(2)` values with and without `min_periods=1`, plus `rolling(3, center=True)` on 5 values |

## I. Categories, chains, performance (Ch. 10–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 49 | Sizes in their real order | drill | code | `sort_by_size(df)` with an ordered categorical `S < M < L < XL`; values outside the list become NA and are counted |
| 50 | Show the empty categories too | applied | code | `orders_per_size(df)` lists **every** size, 0 for unused ones (`observed=False` or `reindex`); measured default hides them |
| 51 | Debug a chain with `tap` | applied | code | `clean_items(items, log)` as one chain calling a `tap(label)` step that appends `(label, shape)` to `log`; the test checks the shapes recorded at each step |
| 52 | Replace a slow group lambda | deep | code | given `transform(lambda s: (s - s.mean()) / s.std())`, write `zscore_by_group(df)` with built-in transforms; equal results; time budget on 300,000 rows (Ch. 12.2) |
| 53 | Long or wide? | applied | explain | which shape for plotting, a printed report, storage, and a groupby; checklist: "tidy/long for analysis", "wide for reading", "melt/pivot", "one fact per row" |

## J. Polars (Ch. 13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 54 | The same question in Polars | applied | code | `revenue_by_region_pl(items: pl.DataFrame)` with `group_by`/`agg`/`sort`; compared with the pandas answer via `.to_dicts()` |
| 55 | Lazy join in Polars | deep | code | `top_products_lazy(items, products)` returns a `pl.LazyFrame` (type checked) joining and aggregating; `.collect()` equals the pandas result |
| 56 | When to switch to Polars | deep | explain | Ch. 13.7–13.8 honestly: size, speed, team, ecosystem; checklist: "measure on your data", "lazy optimisation", "expressions", "pandas ecosystem", "no index" |

## K. Toolkit and project (Ch. 14–15)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 57 | `safe_merge` | challenge | code | the chapter's `safe_merge(left, right, on, how, validate, measure, name)` (Ch. 14.1): validates the relationship, checks the row count for `how="left"`, reports unmatched keys, checks that the `measure` total is unchanged; each guard has a failing test |
| 58 | `reconcile` | applied | code | `reconcile(parts, total, label, tol=0.01)` returns `(ok, difference)`; raises with a readable message when off by more than `tol`; float noise within `tol` passes |
| 59 | New against repeat customers | challenge | code | `new_vs_repeat(orders)` per month: a customer is "new" in the month of their first order; counts and revenue; checked against a loop over customers |
| 60 | Multi-table retail analysis | challenge | code | `assessment = "build"` (project, Ch. 15). `analyse(tables)` → dict answering revenue by region and channel, top 3 per category with unsold products, never-ordered customers, net revenue and return rate, monthly trend; every merge via `safe_merge`, every total reconciled; checked against slow loop computations on a 6-table inline dataset |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 9, 11, 12, 14, 18, 20, 21, 22, 32, 35, 37, 41, 42, 48, 49 = 20 ·
applied 6, 7, 10, 15, 16, 19, 23, 24, 25, 28, 29, 31, 33, 36, 40, 44, 45, 47, 50, 51, 53, 54, 58 = 23 ·
deep 8, 13, 17, 26, 27, 30, 34, 39, 46, 52, 55, 56 = 12 · challenge 38, 43, 57, 59, 60 = 5. Total 60.
Kinds: trace 2, 4, 12, 19, 20, 34, 39, 48 = 8 · explain 13, 30, 53, 56 = 4 · code 48.
Assessments: explain p030, trace p020, fix p026, build p060.

## Risks and open questions

- Group `apply` changed in pandas 2.2–3.x (grouping columns are excluded from what the function sees). Problems check
  results, not methods; solutions should prefer `sort_values` + `head` / `transform` over `apply`.
- p046: confirm on the installed version that `rolling("7D")` needs a sorted `DatetimeIndex` and how it treats the
  first days; write the expected values by hand from the calendar, not from the library.
- p052 and p054/p055 time budgets: Polars is multithreaded; under the runner's 2-thread setting timings change. Keep
  the time check only in p052 (pandas).
- The retail tables in tests must keep the chapter's column names (measured from `make_retail`, Ch. 1.1: `customers` customer_id/city/segment/signup; `products` product_id/category/list_price;
  `stores` store_id/store_city/region; `orders` order_id/customer_id/store_id/order_date/channel; `items` order_id/product_id/qty;
  plus returns): reuse one inline version of them in `conftest.py`. Where a plan line says `price`/`discount`, use
  `list_price` or add the column in that problem's own data and say so in `problem.md`.
