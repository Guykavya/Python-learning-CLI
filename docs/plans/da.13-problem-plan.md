# Problem plan: da.13 Power BI and data modelling (companion) (20 problems)

Rules: [README.md](README.md) (shared, especially R1–R4) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.13.p001`…`p020`, folder `pNNN-slug`.

**Mix:** 7 drill, 6 applied, 5 deep, 2 challenge. **Kinds:** 14 code, 3 trace, 3 explain.
**assessment:** explain = p009, trace = p007, fix = p019, build = p020.
**★ core set (9):** p002, p003, p004, p007, p008, p011, p012, p019, p020.

**Testing notes**
- **There is no Power BI.** Problems are about the *model*: building the star in pandas, checking keys and
  relationships, and writing **DAX measures as strings** that the chapter's **MiniDAX** (`Model`, §4.2) evaluates.
  Expected values always come from pandas on the same data (the §8.3 "grid of contexts against pandas" pattern).
  Power BI Desktop steps (§9.6) are never tested; mention them only as "try it on your machine".
- **Spiked 2026-11-18:** MiniDAX is self-contained: the §4.2 code block (chapter lines ~523–1012, **490 lines**) runs on
  its own (it imports `re`, numpy, pandas, `Decimal`). A 2-table model with `SUM`, `CALCULATE(..., ALL(Product))`,
  `DIVIDE` and `query(group_by, measures)` gave the hand-checked answers (22.0, 15.0, 22.0, 0.318…): **0.8 s, 118 MB**.
  It goes in `conftest.py` (one copy per problem that needs it).
- MiniDAX API: `Model().table(name, df)`, `.relate(many, mcol, one, ocol, active=True, both=False)` (raises if the one
  side is not unique), `.measure(name, expr)`, `.evaluate(expr_or_measure, filters={"Table[Col]": [values]})`,
  `.query(group_by, measures, filters)` → DataFrame. A blank result is `None`.
- **MiniDAX supports:** `SUM SUMX AVERAGE MIN MAX COUNT COUNTROWS DISTINCTCOUNT DIVIDE IF ISBLANK BLANK COALESCE
  CALCULATE FILTER ALL ALLEXCEPT REMOVEFILTERS USERELATIONSHIP VALUES SELECTEDVALUE HASONEVALUE RELATED VAR…RETURN
  SAMEPERIODLASTYEAR DATESYTD DATEADD`. **It does not do:** many-to-many relationships, `ALLSELECTED`, `TREATAS`,
  calculation groups, text/format functions, and **context transition** (a measure called inside an iterator, e.g.
  `SUMX(Product, [Revenue])`). Plan nothing that needs those; `problem.md` lists the supported set.
- Data: a small BrightMart generator (`make_brightmart`, §2.1, `n_orders ≤ 1,500`) and the chapter's `build_star` /
  `build_model` live in conftest for problems that start from a finished model. The learner gets DataFrames or a
  `Model` as arguments (R1). Keys are integers; `DateKey` is `yyyymmdd`.
- Tests compare floats with `pytest.approx(rel=1e-9)`; DAX `BLANK` vs 0 is checked explicitly (`is None`).

## A. Why a model; the star schema (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Five problems of one big table | drill | explain | §2.2: repeated attributes, update anomalies, ambiguous grain, double counting of order-level values (freight), size; answer.md names each with a BrightMart example |
| 2 | Split a flat export into a star | applied | code | `build_star(flat)` (§3.2) → `facts`, `dims` (Product, Store, Customer, Date) with integer surrogate keys; fact rows = flat rows; dimension keys unique; joining back reproduces the flat table's revenue exactly |
| 3 | The checks every model needs | drill | code | `check_star(facts, dims, keys)` (§3.3) → list of issues: duplicate dimension key, fact key missing from its dimension (orphan), null key; three planted faults found, a good star → `[]` |
| 4 | A proper date table | applied | code | `date_table(start, end)` (§3.4): one row per day, no gaps, `DateKey` yyyymmdd, Year, Month, MonthName, Quarter, YearMonth; covers the whole fact range (test passes facts with dates near both ends) |
| 5 | Slowly changing dimension, type 2 | deep | code | `scd2_apply(dim, changes, as_of)` (§3.6): closes the old row (`valid_to`), adds a new current row with a new surrogate key; `lookup_key(dim, natural_key, date)` returns the version valid on that date; history is never overwritten |
| 6 | What is the grain? | drill | trace | `⚠ HAND-TRACE` given code builds a sales fact (one row per order line) and an orders table (one row per order, with freight); predict the printed row counts and the two freight totals (the naive one from the joined table is too high) |

## B. Relationships and filter direction (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 7 | Watch a filter flow | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` a 3-table MiniDAX model (Product 1–* Sales *–1 Store, 8 sales rows); predict `evaluate` results for Revenue with a Product filter, with a Store filter, and `COUNTROWS(Product)` with a Store filter (single direction: still all products) and then with `both=True` |
| 8 | Check the relationships | applied | code | `check_relationships(m)` (§4.7) → DataFrame: relationship, one side unique, blank keys (fact keys with no match), direction, active; a model with an orphan key and a bidirectional link reports both |
| 9 | Why bidirectional filtering is dangerous | deep | explain | `assessment = "explain"`; §4.5: ambiguous paths, filters leaking into unrelated dimensions, numbers that change when a slicer is added; when one-way plus an explicit measure is the fix. Checklist of those points with the §4.4 BrightMart example |
| 10 | The role-playing date | applied | code | `ship_date_measure()` returns the DAX string for revenue by ship date with `USERELATIONSHIP` (inactive Sales[ShipDateKey] → Date[DateKey]); MiniDAX values per year equal the pandas group-by on ship year; the order-date measure is unchanged |

## C. DAX basics (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | The first measures | drill | code | `MEASURES = {"Revenue": "...", "Orders": "...", "Avg order value": "..."}` (SUMX with discount, DISTINCTCOUNT, DIVIDE); each checked on a grid of contexts (year × category × region, §8.3) against pandas |
| 12 | CALCULATE and ALL | applied | code | measures "Kitchen revenue" (`CALCULATE([Revenue], Product[Category] = "Kitchen")`) and "% of all revenue" (`DIVIDE([Revenue], CALCULATE([Revenue], ALL(Product)))`); grid against pandas; under a Category filter "Kitchen revenue" ignores it (message explains filter replacement) |
| 13 | Share within the category: ALLEXCEPT | deep | code | "% of category" with `ALLEXCEPT(Product, Product[Category])` (§5.5); per product the shares within a category sum to 1; compared with pandas `groupby(...).transform("sum")` |
| 14 | DIVIDE, blanks and COALESCE | drill | trace | `⚠ HAND-TRACE` MiniDAX on five expressions over a tiny model: `DIVIDE` by a zero total, a measure for a filter with no rows (`None`, printed as `BLANK`), `COALESCE([x], 0)`, `IF(ISBLANK(...))`, `VAR … RETURN`; predict the printed values. Run them before shipping |
| 15 | Time intelligence | challenge | code | "Revenue PY", "Revenue YTD", "YoY %" (§5.7, `SAMEPERIODLASTYEAR`, `DATESYTD`, `DIVIDE`); for each month of 2024, PY equals the pandas 2023 month; YTD is a running sum that restarts in January; YoY blank for the first year |
| 16 | Calculated column or measure? | drill | explain | §5.1: for six needs (price band per product, margin %, running total, customer age group, distinct customers, revenue per store) say column or measure and why (row context vs filter context, stored vs computed at query time) |

## D. Modelling patterns (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | A budget at a coarser grain | deep | code | §6.1: budget per (month, category) related through the Date and Product dimensions via bridge keys; "Budget" and "Actual vs budget %" measures; by category and month they match pandas; at product level the budget is blank (not repeated) and the message says why |
| 18 | Non-additive measures done right | applied | code | "Margin %" as `DIVIDE([Margin], [Revenue])` (ratio of sums) against the wrong "average of the per-line margin" (§6.2–6.3); test shows they differ on the data and that only the ratio of sums equals pandas at every grid level |

## E. Testing a model; the project (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Fix the broken model | deep | code | `assessment = "fix"`; given a `build_model()` with three faults from §8.3's `broken()` catalogue (Sales–Store relationship missing, an `ALL(Product)` left in Revenue, the discount forgotten); fix it. Tests: `test_measures` grid against pandas (§8.3) passes, `reachability` (§8.2) shows every measure changes with every dimension, `lint_model` (§8.4) → `[]` |
| 20 | From specification to a tested model | challenge | code | `assessment = "build"`; `model_from_project(folder)` (§9.4): reads the tables (CSV or Parquet) and a JSON spec (relationships, measures) that the test writes into `tmp_path`, builds the `Model`; tests: the spec's expected values (§9.5) match, `check_report_spec` (§9.3) passes for a report spec, a spec with a duplicate key on the one side fails with a clear message |

## Counts check

Tiers: drill 7 (1, 3, 6, 7, 11, 14, 16) · applied 6 (2, 4, 8, 10, 12, 18) · deep 5 (5, 9, 13, 17, 19) · challenge 2 (15, 20) = 20.
Traces 3: 6, 7, 14. Explain 3: 1, 9, 16. Code 14. One assessment of each kind: explain 9, trace 7, fix 19, build 20.

## Risks and open questions

- MiniDAX is the chapter's model of DAX, not Power BI. Every trace output (p6, p7, p14) must come from running MiniDAX.
- No context transition: never write `SUMX(Dim, [Measure])`. If a learner writes one, MiniDAX gives a wrong number
  or an error; `mistakes.md` of p11–p13 should say so.
- p20 reads Parquet: pyarrow must be importable (it is; shared.02 uses it). The test writes the files itself.
- conftest.py with MiniDAX (~490 lines) is duplicated in ~14 problems; same maintenance note as da.12.
