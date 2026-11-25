# Check the finished report

Chapter section 7.4. The report itself needs tests: the numbers in the text must be the computed ones, every figure must exist (and every figure made should be used), nothing may be left
from the template, and the report must not claim older data than it used.

Write `check_report(md_text, numbers, figures_dir, data_to)`. It returns a list of problems (empty when the report is fine), in this order:

1. For each `name, text` in `numbers` (a dict of already formatted strings such as `{"churn_after": "5.7%"}`), in dict order: if `text` is not in the report,
   `"{name} = {text} does not appear in the text"`.
2. If the text contains `{` or `}` or `TODO`: `"unfilled template placeholder or TODO left in the text"` (once).
3. For each image reference `![...](FILE)` in the text, in order of appearance: if `figures_dir / FILE` does not exist, `"figure file missing: FILE"`.
4. For each `.png` file in `figures_dir` (sorted by name) that the text never references: `"figure not used in the text: FILE"`.
5. The report must contain a line `Data to: YYYY-MM-DD`. If it is missing: `"no 'Data to:' line"`. If its date is **earlier** than `data_to` (a string in the same format):
   `"stale date: text says {date}, data run to {data_to}"`.

## Example

A report that says `5.1%` where `numbers` has `5.7%`, references `missing.png` and says `Data to: 2024-11-30` while the data run to `2024-12-30` gives three problems.
