# Customer analytics case study

Chapter section 7. The project: four analyses, one recommendation page, **every number computed from the data**, and a check that nothing on the page was edited by hand afterwards.

`starter.py` already has the pieces from the module (given, do not change): `Finding` and `lint_finding` (section 6.4), `two_prop` (problem 5), `repeat_rate_90d` (problem 19), `rfm_table`, `score_quantile`, `segment` (problems 23 and 24), the list `SEGMENTS` and the
regular expression `DEC` for decimal numbers. `data` is a dict: `exp` (columns `variant`, `converted`, `revenue`), `sessions` (`device`, `added_to_cart`, `started_checkout`, `purchased`), `customers` (`customer_id`, `first_order`, `channel`),
`orders` (`customer_id`, `order_date`, `amount`) and `asof`.

**1. `build_case_study(data)`** returns `(finding, page, results)`:

- A/B test: `two_prop` on conversion; `ab_text = "{diff:+.2f} points (95% CI {lo:+.2f} to {hi:+.2f})"` with the difference and limits in **percentage points**;
- funnel: the share of mobile (and of desktop) carts that started checkout; `fun_text = "{mobile:.0f}% against {desktop:.0f}%"`;
- retention: the 90-day repeat rate (`rate_pct`) **per channel**, each customer group using only its own customers and orders; lines `"{channel}: {rate:.1f}%"`, channels sorted;
- RFM: scores as in the chapter (`R` with `score_quantile(..., higher_is_better=False)`, `F` with `pd.cut(F, [0, 1, 2, 3, 5, inf], labels=1..5)`), `segment(r, f)`, the number of customers per segment in the order of `SEGMENTS`, lines `"{segment}: {n:,}"`;
- `finding`: a `Finding` whose headline contains `fun_text`-style numbers and the A/B difference, with at least two recommendations (owner and a date like `31 March 2025`), an impact **range**, three evidence items with numbers (one with its 95% CI),
  a confidence statement, two limitations and a success measure in the next steps. `lint_finding(finding)` must find **no** problems (at most 450 words);
- `page`: `finding.render_markdown()`, then a section `## Retention by channel (90-day repeat rate)` with the channel lines and a section `## RFM segments (customers)` with the segment lines;
- `results`: a dict with `"expected"` (the list: `ab_text`, `fun_text`, then the channel lines, then the segment lines), `"decimals"` (the sorted list of the decimal numbers found in `page` by `re.findall(DEC, page)`), and also `"ab"`, `"funnel"`, `"repeat"` (dict channel to rate) and `"segments"` (dict segment to count).

**2. `check_case_study(page, results)`** returns a list of problems: first `"missing: <text>"` for each string of `results["expected"]` that is not in `page` (in that order), then `"number not in the results: <token>"` for each decimal number
of the page (in order of appearance, each once) that is not in `results["decimals"]`.

## Example

If someone edits the funnel sentence on the page after the build, `check_case_study` reports `missing: 45% against 66%` and the new number as `number not in the results`.
