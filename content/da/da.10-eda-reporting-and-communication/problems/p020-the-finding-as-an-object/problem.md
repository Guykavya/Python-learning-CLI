# The finding as an object

Chapter sections 6.2 to 6.4. **No number is typed by hand in the text.** Every number of the finding comes from a dictionary `R` filled by the analysis, so that the text
follows when the data change. The finding is a `Finding` object (in `starter.py`; keep it as it is) with the sections of the template.

Write `make_finding(R)`. `R` has the keys `churn_before`, `churn_after`, `ontime_before`, `ontime_after` (percent), `saved`, `saved_lo`, `saved_hi` (customers a month),
`rr`, `rr_lo`, `rr_hi` (rate ratio and its 95% CI) and `late_pts`, `late_pts_lo`, `late_pts_hi` (points of churn due to late boxes). The finding must:

- have a headline that contains `{churn_before:.1f}%`, `{churn_after:.1f}%`, `{ontime_before:.0f}%` and `{ontime_after:.0f}%`;
- have an impact that contains `about {saved:.0f} customers (range {saved_lo:.0f} to {saved_hi:.0f})`;
- have an evidence item that contains `{rr:.1f} times as often (95% CI {rr_lo:.1f} to {rr_hi:.1f})` and one that contains
  `{late_pts:.1f} points (95% CI {late_pts_lo:.1f} to {late_pts_hi:.1f})`;
- pass the chapter's `lint_finding` (shown in `conftest.py` and in section 6.4) with **no** issues: owners and dates (`31 January 2025`) for the recommendations, a confidence statement,
  at least two limitations, a success measure in the next steps, and none of the vague phrases.

## Example

With the chapter's `R` the headline can read `Monthly churn rose from 4.0% to 5.7% in Sep-Dec 2024, almost entirely because on-time delivery fell from 92% to 80%`.
