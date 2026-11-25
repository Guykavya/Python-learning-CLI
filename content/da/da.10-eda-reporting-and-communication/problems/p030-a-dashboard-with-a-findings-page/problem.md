# A dashboard with a findings page

Chapter section 9 (the project). The rule of the chapter: **the dashboard only displays; the logic lives in functions with tests.** Then the dashboard and the written report can never disagree.

`solution.py` holds both. Write the **logic functions** first:

| function | returns |
|---|---|
| `filter_data(customers, panel, channels, plans, cities)` | `(customers, panel)` of the chosen segments, or `None` if any list is empty or no panel rows remain (problem 28) |
| `monthly_kpis(customers, panel)` | per month (`Period` index): `opening_actives`, `churned`, `churn_rate_pct`, `on_time_pct` (problem 6, without revenue) |
| `baseline(kpis, start="2024-04", end="2024-08")` | `{"churn": mean churn_rate_pct, "on_time": mean on_time_pct}` over those months, as floats |
| `finding_text(kpis, base)` | `"In {last month}, monthly churn was {c:.1f}% against {base churn:.1f}% in the baseline period ({c - base churn:+.1f} points); {o:.0f}% of boxes arrived on time against {base on_time:.0f}%."` |

Then the **app**, `main(customers, panel)`:

- title `FreshBox: churn dashboard` and a caption with the churn definition (`CHURN_NOTE`);
- in the sidebar, three multiselects `Channel`, `Plan`, `City` with the sorted values, all selected by default;
- empty or impossible selection: `st.warning("Select at least one value in every filter.")` and nothing else;
- otherwise two tabs, `Findings` (`st.markdown(finding_text(...))`) and `Explore` with three metrics for the **last month**:
  `Opening actives, {month}` (`f"{n:,}"`), `Monthly churn, {month}` (`f"{c:.1f}%"`, with a delta against the baseline) and `Boxes on time, {month}` (`f"{o:.0f}%"`), and a line chart of the churn rate.

`demo_data()` and the `__main__` block are given, so `streamlit run solution.py` works on your machine. The tests run the app with a small FreshBox data set (`conftest.py`).

## Example

With every filter selected, the churn metric shows the last row of `monthly_kpis(customers, panel)`, for example `6.5%`; selecting only `paid` changes it to the paid customers' rate.
