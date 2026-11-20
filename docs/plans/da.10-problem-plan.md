# Problem plan: da.10 EDA, reporting and communication (30 problems)

Rules: [README.md](README.md) (shared, especially R1–R4) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.10.p001`…`p030`, folder `pNNN-slug`.

**Mix:** 10 drill, 10 applied, 7 deep, 3 challenge. **Kinds:** 21 code, 5 trace, 4 explain.
**assessment:** explain = p004, trace = p011, fix = p023, build = p030.
**★ core set (12):** p001, p004, p006, p008, p010, p013, p016, p018, p022, p023, p027, p030.

**Testing notes**
- Data: a **small** FreshBox generator (`make_freshbox`, §2.1, with `n ≤ 1,500` customers) lives in `conftest.py`
  and is passed in as `customers, panel`. Hand-checkable problems use 6–12-row inline tables.
- **Streamlit spiked 2026-11-18** under the runner's limits (pandas + streamlit, tiny app): **2.8 s, 160 MB**.
  What works:
  - `AppTest.from_file("solution.py", default_timeout=30).run()` runs the file **as `__main__`**, so the app layout is
    `def main(df=None): ...` plus `if __name__ == "__main__": main()`. The test can also `import solution` to unit-test the
    logic functions (only a harmless "missing ScriptRunContext" warning is printed).
  - Widgets: `at.multiselect[0].set_value([...]).run()`, `at.selectbox`, `at.slider`, `at.date_input` likewise.
  - Read back: `[m.value for m in at.metric]` (strings, e.g. `'35.0'`), `[m.label for m in at.metric]`,
    `at.title[0].value`, `[m.value for m in at.markdown]`, `[i.value for i in at.info]`, `at.exception` (empty when fine),
    `at.dataframe[0].value` (a DataFrame).
  - **Injecting test data:** `AppTest.from_function(app)` where `app()` does `from solution import main; main(df)`:
    the test's own small DataFrame reaches the app, so the app never reads a file (R1).
- The chapter's `Finding` dataclass, `lint_finding` (§6.4, list of exact issue strings, `VAGUE` phrase list) and
  `render_markdown` are given in `problem.md`/conftest and used as specs. `lint_finding` messages are compared as
  exact strings, so copy them from the chapter.
- `fingerprint(df)` (§7.3) uses `pd.util.hash_pandas_object`; its hex value can change between pandas versions.
  Tests check **properties** (same data → same fingerprint; one changed cell → different; row order matters), never a hash string.
- Matplotlib for p019: `matplotlib.use("Agg")`, inspect the returned figure (see da.09 notes).

## A. From data to decision; the one-page finding (Ch. 1, 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Answer first | drill | code | `answer_first(question, number, comparison, unit)` → one headline sentence with the number and a comparison word ("from 4.1% to 6.3%"); the chapter's headline checks (number present, comparison word, ≤ 40 words) |
| 2 | Actionable or not? | drill | trace | `⚠ HAND-TRACE` run `lint_finding` on four small `Finding` objects (given code); predict the printed issue lists |
| 3 | Rewrite the vague finding | drill | explain | a vague paragraph ("engagement appears to be somewhat down") → rewrite as headline + recommendation + impact range; answer.md: model rewrite + checklist (number, comparison, owner, date, range in business units, limitation) |
| 4 | What makes a finding actionable? | applied | explain | `assessment = "explain"`; explain to a new analyst why "answer first, with owner, date, range and limitations" is the template (§1.2–1.4). Checklist: decision it changes, who acts, by when, how big (range), how sure, what could make it wrong |

## B. KPIs and metrics (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Check a KPI definition | drill | code | `check_kpi(defn)` → list of messages for a KPI definition dict (name, numerator, denominator, grain, owner, direction, type in leading/lagging/vanity/guardrail): missing field, unknown type, a ratio with no denominator; a complete definition → `[]` |
| 6 | Monthly KPIs | applied | code | `monthly_kpis(customers, panel)` (§3.4): active customers, orders per active, churn rate per month; tiny inline data with hand answers; months with no customers → NaN, not 0 |
| 7 | A KPI tree that adds up | applied | code | `revenue_tree(df)` → revenue = active × orders per active × average order value per month; the product equals revenue within 1e-9 for every month (message names the month that fails) |
| 8 | Guardrail breaches by hand | drill | trace | `⚠ HAND-TRACE` the given `guardrail_breaches(kpis, limits)` on a 4-month KPI table with one value exactly on a limit (inclusive rule in the code); predict the printed `(month, kpi, value)` lines |

## C. Hypothesis-driven EDA (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Before and after by hand | drill | trace | `⚠ HAND-TRACE` given code splits an 8-week churn table at a date (the split week counts as "after") and prints both means `:.2f`; predict them |
| 10 | Cut by segment | applied | code | `segment_table(o, dim)` (§4.4): churn rate before/after per segment, change in points, share of customers; sorted by change; NaN-free |
| 11 | Mix against rate by hand | deep | trace | `assessment = "trace"`; `⚠ HAND-TRACE` two segments, before/after shares and rates in a 4-row table; the chapter's `mix_rate_decomposition` printed (`:.2f` points): mix, rate, total, and `mix + rate == total` |
| 12 | Mix–rate decomposition | deep | code | `mix_rate_decomposition(o, dim)` (§4.5, symmetric weights); the two effects add up to the total within 1e-9; a pure mix change → rate effect 0; a pure rate change → mix effect 0 |
| 13 | Season and the base year | applied | code | `yoy_change(series)` compares each month with the same month a year earlier, not the previous month; first year → NaN; a seasonal series with no trend gives ≈ 0 change |
| 14 | Which hypothesis first? | drill | explain | given 5 hypotheses for a churn rise, order them by (cheap to test, size of possible effect) and say which data each needs (§4.3) |

## D. Testing the hypotheses (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Rate ratio with an interval | applied | code | `rate_ratio(e1, n1, e0, n0)` (§5.2) → ratio and 95% CI on the log scale; hand example to 3 decimals; zero events → `ValueError` with a message |
| 16 | Holding other things equal | deep | code | `late_effect(df)` with a logistic model (`smf.logit`) or the chapter's `design()` + statsmodels: the adjusted odds ratio for `late` with CI; on the conftest world (true effect known) the CI contains it; the naive ratio is further away |
| 17 | A natural experiment | deep | code | `price_change_effect(panel, change_date, window_weeks)`: difference-in-differences between affected and unaffected plans; hand data with a known +2 point effect |
| 18 | The evidence table | applied | code | `evidence_table(results)` → DataFrame with hypothesis, estimate, CI, verdict ("supported", "not supported", "inconclusive" by the CI rule); exact labels |
| 19 | A figure for the page | applied | code | `fig_contributions(summary)` (§6.5): horizontal bars sorted, one bar per cause, title states the largest contributor, x label in points; tested by figure properties |

## E. Writing and rendering the finding (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | The finding as an object | drill | code | build a `Finding` from a results dict (`make_finding(R)`, §6.3) so that `lint_finding(f) == []`; the numbers in the text come from `R`, not typed by hand (test changes `R` and expects the text to change) |
| 21 | Different readers, same numbers | drill | explain | rewrite one long finding (given) as a 3-sentence message for the CEO and a bullet list for the operations lead, with the **same rounded numbers** (§6.7); answer.md shows both and the checklist: same numbers, decision first, no method detail for the CEO, owner and date for operations |
| 22 | Render the page to HTML | challenge | code | `render_html(f, source_note)` (§6.6): escapes `<` and `&` in text (`html.escape`), one `<h3>` per section, figures embedded as base64 `<img>` read from `tmp_path` |
| 23 | Fix the lying report | deep | code | `assessment = "fix"`; given a `build_report(R)` that hard-codes two numbers, rounds the CI differently from the estimate and drops limitations when the list is long; fix it. Tests: numbers follow `R`, same rounding rule everywhere, all limitations present, `lint_finding` clean |

## F. Reports as code (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Re-run for any date | deep | code | `quick_summary(customers, panel, as_of)` (§7.2) uses only data up to `as_of` (test adds future rows: result must not change, message "future data leaked into the report") |
| 25 | Provenance fingerprint | applied | code | `provenance(frames, analysis_date)` → dict of row counts, date range, fingerprints; properties only (same → same, changed cell → different, R3) |
| 26 | Check the finished report | challenge | code | `check_report(md_text, R, figures_dir)` (§7.4) → list of problems: number in text not in `R`, missing figure file, figure referenced but absent, stale date |

## G. Streamlit dashboards and the project (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | A first tested app | drill | code | `solution.py` is a Streamlit app: title, a city multiselect, a revenue `st.metric`; AppTest checks default metric, the value after selecting one city, and the empty-selection message (`st.info`), and that `at.exception` is empty |
| 28 | Filters as a pure function | applied | trace | `⚠ HAND-TRACE` the chapter's `filter_data` (§9.2) on an 8-row table with three filter combinations, including an empty list (meaning "no rows", not "all rows"); predict printed row counts |
| 29 | Cache the expensive step | deep | code | app uses `@st.cache_data` for loading; test counts calls of the loader across two reruns with AppTest (a counter in `st.session_state` or a module global the reference documents) → called once |
| 30 | A dashboard with a findings page | challenge | code | `assessment = "build"`; logic functions (`filter_data`, `monthly_kpis`, `baseline`) + `main(customers, panel)` app with sidebar filters, KPI metrics against the baseline, a chart and a findings tab rendered from `Finding`. Tests: logic unit tests on tiny data; AppTest via `from_function` with test data: default metrics equal the logic's numbers, changing a filter changes them, empty selection shows a message, no exception on a 3×3 smoke grid of filters (keep under 20 s) |

## Counts check

Tiers: drill 10 (1, 2, 3, 5, 8, 9, 14, 20, 21, 27) · applied 10 (4, 6, 7, 10, 13, 15, 18, 19, 25, 28) ·
deep 7 (11, 12, 16, 17, 23, 24, 29) · challenge 3 (22, 26, 30) = 30.
Traces 5: 2, 8, 9, 11, 28. Explain 4: 3, 4, 14, 21. Code 21. One assessment of each kind: explain 4, trace 11, fix 23, build 30.

## Risks and open questions

- AppTest timing: the chapter uses `default_timeout=120` for the full dashboard; under the runner budget the
  build test must use small data (n ≤ 1,500) and at most ~9 reruns. Measure the reference: it must finish in ≤ 20 s.
- `st.cache_data` persists across AppTest runs *within one process*; tests that count loader calls must clear it
  (`st.cache_data.clear()`) at the start.
- p16 depends on statsmodels' logit converging on small data; use n ≥ 1,000 and a clear effect.
- Streamlit widget accessors change between versions; the reference pins the ones confirmed above.
