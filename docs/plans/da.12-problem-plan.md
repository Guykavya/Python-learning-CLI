# Problem plan: da.12 Excel for analysts (30 problems)

Rules: [README.md](README.md) (shared, especially R1–R4) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.12.p001`…`p030`, folder `pNNN-slug`.

**Mix:** 10 drill, 10 applied, 7 deep, 3 challenge. **Kinds:** 23 code, 4 trace, 3 explain.
**assessment:** explain = p026, trace = p002, fix = p014, build = p030.
**★ core set (12):** p001, p002, p005, p006, p007, p009, p013, p014, p018, p020, p025, p030.

**Testing notes**
- **There is no Excel.** The learner's Python builds an `openpyxl.Workbook` with **formulas as text** and returns it
  (or saves it to a `tmp_path` the test passes in). The test evaluates the formulas with the chapter's **MiniXL**
  (`Book`, §4.1) and compares with the pandas truth (`reference()`, §3.2). Excel stays "the final authority", as the
  chapter says; MiniXL is the offline judge.
- **Spiked 2026-11-18:** an openpyxl-saved file has **no cached values**: `load_workbook(path, data_only=True)["Data"]["D1"].value`
  is `None`, and without `data_only` it is the formula text. MiniXL evaluated `SUMIFS`, `XLOOKUP` and a wildcard `COUNTIFS`
  correctly on an **in-memory** workbook (`Book(wb).value("Data", "D1")`), no save needed: **1.0 s, 118 MB** with pandas.
- **MiniXL goes in `conftest.py`, ~610 lines.** Copy chapter lines 14–21 (the header imports: `re`, `dt`,
  `openpyxl`, `get_column_letter`, `to_excel/from_excel`, `DefinedName`) **plus** the code block of §4.1 (from
  `import math` at line ~330 to the closing fence at ~937). The §4.1 block alone fails with `NameError: re` and then
  `column_index_from_string`: it relies on the chapter's first block. Expose it with a fixture
  (`@pytest.fixture def xl(): return Book`). Every problem that evaluates formulas carries the same `conftest.py`;
  write it once, copy it.
- MiniXL implements only: `SUM AVERAGE COUNT COUNTA MIN MAX ABS ROUND IF IFERROR IFNA ISERROR TRIM TEXT DATE YEAR
  MONTH SUMIFS COUNTIFS AVERAGEIFS SUMIF COUNTIF LARGE MATCH INDEX XLOOKUP VLOOKUP`, cell/range references, defined
  names and error propagation. **Plan no formula outside that list.** `problem.md` says so ("the checker knows these functions").
- Data: a small `make_homegoods` (§3.1, `n ≤ 400` orders, `n_cust ≤ 40`) in conftest; tiny inline tables for
  hand-checked problems. Keep workbooks ≤ 500 rows: MiniXL is a pure-Python evaluator, and a 3,000-row SUMIFS grid
  is slow (measure the reference; target ≤ 10 s).
- Formula text comparisons normalise case and spaces only; tests prefer evaluating to comparing text, so equivalent
  formulas pass. Where the *form* matters (absolute `$` references, exact-match lookups) the test checks the text too
  and says why.
- Files: when a problem saves, the path comes from the test (`tmp_path / "report.xlsx"`); `.xlsx` files in
  `my-work/` are not copied by the runner (README R1).

## A. The workbook as data (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Dates are numbers ✅ | drill | code | `to_serial(d)` / `from_serial(n)` equal openpyxl's `to_excel` / `from_excel` for dates from 1900-03-01 on; times as fractions of a day; message for an off-by-one ("Excel counts 1900-01-01 as day 1 and keeps a fake 29 Feb 1900") |
| 2 | A formula has no value until Excel runs it ✅ | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` given code writes `=SUM(A1:A3)`, saves, reloads with and without `data_only=True` and also reads it with `pandas.read_excel`; predict the printed values (`None`, the formula text, `NaN` as printed by `float(...)`). Spiked: `None` and the text are confirmed |
| 3 | Types that look alike ✅ | applied | code | `audit_column(ws, col)` → counts of numbers, numbers stored as text (`"12"`), blanks, empty strings, dates; test builds a sheet with each kind |
| 4 | Excel rules a pandas user must know ✅ | drill | explain | pick four of the §4.2 rules (SUM skips text numbers, blank vs 0 in AVERAGE, ROUND half away from zero, criteria are case-insensitive) and give for each the pandas expression that would give a *different* number |
| 5 | Round like Excel ✅ | drill | code | `xl_round(x, n)` (§4.1: take the value at 15 significant digits, `Decimal(format(x, ".15g"))`, then half away from zero); `xl_round(2.5) == 3`, `xl_round(-2.5) == -3`, `xl_round(0.125, 2) == 0.13`, `xl_round(1.005, 2) == 1.01` where Python's `round` gives 1.0; messages: "Python's `round` rounds half to even" and "the float 1.005 is stored as 1.00499…; Excel looks at 15 digits" |

## B. Formulas for analysts (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Calculated columns with an absolute reference ✅ | applied | code | `add_margin_column(ws, n_rows, rate_cell="$M$1")` writes `=F2-G2*$M$1` style formulas row by row; MiniXL values equal pandas; text check that every row uses `$M$1` (message: "without `$`, the reference moves when the formula is filled down") |
| 7 | Find the overwritten formula ✅ | applied | code | `column_consistency(ws, col, first_row)` (§5.3) → rows where a formula differs from the column pattern (compared after replacing the row number) or a typed number replaced the formula; two planted faults found, a clean column → `[]` |
| 8 | Named ranges ✅ | applied | code | `set_names(wb, n_rows)` defines `Rev`, `Region`, `Cat` over the data rows; `=SUM(Rev)` evaluated by MiniXL equals pandas; after appending rows and calling it again, the names cover the new rows |

## C. Conditional aggregation (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | One SUMIFS formula for the whole grid ✅ | applied | code | `add_grid(wb, regions, cats, top, left)` (§6.3): mixed references (`$A8`, `B$7`) so one formula fills the grid; every cell equals `pivot_table(..., aggfunc="sum")`; a region/category with no rows → 0 |
| 10 | The criteria language by hand ✅ | drill | trace | `⚠ HAND-TRACE` MiniXL evaluates `COUNTIFS` on 8 inline cells with the criteria `">=10"`, `"<>North"`, `"N*"`, `"north"`, `""` (blank) and `"="`; predict the counts. Run it through MiniXL before shipping |
| 11 | The average of averages ✅ | deep | code | `add_price_metrics(wb)` writes both "average list price" (`AVERAGEIFS`) and "revenue per unit" (`SUMIFS/SUMIFS`) for one region; both equal their pandas versions; the test asserts they differ on the data (§6.4) |
| 12 | Errors you will meet ✅ | drill | trace | `⚠ HAND-TRACE` MiniXL on five formulas: a division by a blank, `XLOOKUP` of a missing key, `IFERROR` around it, `IFNA` around a `#DIV/0!`, and `SUM` of a range containing `#N/A`; predict the printed values/errors |

## D. Lookups (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | XLOOKUP and INDEX/MATCH ✅ | drill | code | `add_price_lookup(wb, how)` with `how="xlookup"` or `"index_match"`; both give the pandas merge result; a missing product shows `"not found"` (XLOOKUP's 4th argument / `IFNA`) |
| 14 | The approximate-match trap ✅ | deep | code | `assessment = "fix"`; given a builder using `VLOOKUP(key, table, 2)` (4th argument missing → approximate match) on **unsorted** product codes, so some prices are silently wrong; fix to exact match. Tests: every price equals the pandas merge; the formula text has `FALSE`/`0` as 4th argument or uses XLOOKUP |
| 15 | Duplicate and dirty keys ✅ | applied | code | `key_report(keys)` → duplicates, keys with leading/trailing spaces, case variants, numbers stored as text; run before writing any lookup (§7.3) |
| 16 | A lookup is a left join ✅ | deep | explain | a product code appears twice in the price table: what VLOOKUP returns, what `merge` returns, and why the totals differ (§7.5 fan-out rules) |
| 17 | Top-N with LARGE, INDEX and MATCH ✅ | challenge | code | `add_top3(wb)` lists the three best products with revenue; with a tie in revenue the formula must still list three **different** products (tie-break helper column, §7.4); compared with `nlargest(3, keep="first")` |

## E. PivotTables and Power Query (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Check a pasted pivot ✅ | applied | code | `check_pivot(expected, pasted, tol)` (§8.3) → list of mismatches `(row, col, expected, got)`; normalises "Grand Total" and `(blank)` labels; a pasted pivot with one wrong cell and one missing row is caught |
| 19 | The pivot's numbers in pandas ✅ | drill | code | `pivot_expected(orders)` → `pivot_table` with `margins=True, margins_name="Grand Total"`, revenue rounded to 2 decimals, the row order Excel uses (alphabetical) |
| 20 | Power Query steps in pandas ✅ | applied | code | `apply_steps(df, steps)` runs a list of step dicts (§9.4: promote headers, trim, change type, filter blanks, unpivot, group) on the §9.2 messy source; result equals the hand-written expected table; unknown step → `ValueError` naming it |
| 21 | Verify a query without running it ✅ | deep | code | `fingerprint_table(df, keys)` (§9.6) → row count, numeric column sums, distinct keys, blanks; `compare_fingerprints(a, b)` lists the differences in plain words |
| 22 | A folder of files ✅ | applied | code | `combine_folder(folder)` (§9.5): every CSV in a folder the test writes into `tmp_path`, with a `source` column; repeated header rows and empty files skipped; files read in sorted order |

## F. Automating Excel with openpyxl (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | A formatted table ✅ | drill | code | `write_df(ws, df, formats)` (§10.1): bold header, number formats (`#,##0.00`, `yyyy-mm-dd`), freeze panes at `A2`, column widths; test reads `cell.number_format`, `ws.freeze_panes`, `cell.font.b` |
| 24 | Conditional formatting and validation ✅ | applied | code | margin below target highlighted (a `CellIsRule` or formula rule on the margin column), a list validation on the region input cell; test inspects `ws.conditional_formatting` and `ws.data_validations.dataValidation[0].formula1` |
| 25 | Text that looks like a formula ✅ | deep | code | `safe_text(value)` (§10.7): user text starting with `=`, `+`, `-`, `@` is stored as text, never as a formula; numbers and dates untouched; the test reloads the saved file and checks `cell.data_type` |
| 26 | Generate, do not edit ✅ | deep | explain | `assessment = "explain"`; why the report is rebuilt from Python each time instead of being opened, edited and saved by a script: cached values vanish (§10.5), round trips lose things (§10.6), and the numbers can no longer be traced to pandas. Checklist of those three points plus "what a reader of the file sees before Excel recalculates" |

## G. When the numbers do not match; the project (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Control total and bridge ✅ | challenge | code | `bridge(clean, dirty)` (§11.2–11.4): the total difference split into causes (duplicates, text numbers, wrong region spelling, missing rows) whose amounts **sum to the gap** exactly; a dirty copy from a small `make_dirty` in conftest |
| 28 | Clean once, with a log ✅ | deep | code | `clean_orders(df, regions, valid_codes)` (§11.5) → clean frame + log rows `(row, field, old, new, rule)`; after cleaning, the Excel total (via MiniXL on a workbook built from the clean frame) equals pandas |
| 29 | The last decimal ✅ | drill | trace | `⚠ HAND-TRACE` §11.6: the sum of rounded values vs the rounded sum on 4 inline amounts, then `xl_round` vs `round` on `0.125`, `2.5`, `1.005`, `2.675` (spiked: `xl_round` gives 0.13, 3.0, 1.01, 2.68; `round` gives 0.12, 2, 1.0, 2.67); predict the printed lines |
| 30 | A report generated and refreshed from Python ✅ | challenge | code | `assessment = "build"`; `build_report(orders, customers, products, target_margin)` (§12.1) → Workbook: data sheet, named ranges, SUMIFS summary grid, lookup column, conditional format. Tests: `verify_report` (§12.2) via MiniXL equals the pandas reference; `lint_workbook` (§12.3) finds nothing; rebuilt with a second, longer dataset the names grow and values still match (§12.4) |

## Counts check

Tiers: drill 10 (1, 2, 4, 5, 10, 12, 13, 19, 23, 29) · applied 10 (3, 6, 7, 8, 9, 15, 18, 20, 22, 24) ·
deep 7 (11, 14, 16, 21, 25, 26, 28) · challenge 3 (17, 27, 30) = 30.
Traces 4: 2, 10, 12, 29. Explain 3: 4, 16, 26. Code 23. One assessment of each kind: explain 26, trace 2, fix 14, build 30.

## Risks and open questions

- MiniXL's behaviour on edge criteria (blank vs empty string, `"="`) is the chapter's model of Excel; p10 and p12
  outputs must be produced by running MiniXL, never written from memory of Excel.
- `conftest.py` duplicated in ~20 problems (≈ 23 KB each). If the chapter's MiniXL ever changes, every copy must
  change. A shared helpers folder would need an engine change (not done; ask Kavya).
- p5/p29 rest on the chapter's `xl_round` (15 significant digits, then half up). Values above were run on 2026-11-18; re-run the trace code when writing, as always.
  whatever it really prints.
- PivotTables and Power Query cannot be created or run offline; their problems check the numbers (p18–p22), never
  the Excel objects. Say so in each `problem.md`.
