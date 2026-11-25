## Hint 1

Split the work: one small function per chart that returns `(fig, title)`, then one function that collects them. Write the **data step** (the numbers for the title) before the drawing step, and
check each title by hand on a tiny table.

## Hint 2

```text
trend:      monthly sums; year totals Y0, Y1 -> word, pct
stores:     totals sorted ascending; top = last, bottom = first
categories: totals sorted descending; share of the total
weekdays:   daily totals per date, mean by day_of_week, names Monday..Sunday
build_report: for each: savefig(...) then plt.close(fig) in finally; then write report.md
```
