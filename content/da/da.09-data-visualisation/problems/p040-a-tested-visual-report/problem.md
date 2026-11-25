# A tested visual report

Chapter section 10 (the project). A visual report is code: one function per chart, titles and alt text **computed from the data**, every figure checked by a linter, and the files written
for you to share. Build a small version.

`sales_df` has the columns `date`, `store`, `category`, `units` and `revenue` (two whole calendar years, one row per date, store and category).

**1. `make_figures(sales_df)`** returns a list of four tuples `(name, fig, alt)`, in this order:

| name | chart | title (computed from the data) |
|---|---|---|
| `trend` | line of monthly revenue, y from 0, y label `Monthly revenue (USD)`, x label `Month` | `Revenue grew 11% from 2023 to 2024` (`grew` or `fell`; the percent is `round(abs(Y1 / Y0 - 1) * 100)` with `Y` the revenue of the first and the last calendar year) |
| `stores` | horizontal bars of total revenue per store, smallest at the bottom, x from 0 | `Airport earns 1.5 times as much as Mall` (largest and smallest store; ratio of totals with one decimal) |
| `categories` | vertical bars of total revenue per category, largest first, y from 0 | `espresso is the largest category (64% of revenue)` (share with no decimals) |
| `weekdays` | vertical bars of the **average daily revenue** (all stores and categories added per date) for Monday ... Sunday in that order, y from 0 | `Saturday is the busiest weekday` (full English day name) |

Every figure needs axis labels with units, and **must pass the chart linter** (a copy is in `conftest.py`: no missing title or labels, bars from 0, readable fonts).
The `alt` text is `"<kind>. <title>."` with `kind` = `Line chart of monthly revenue`, `Bar chart of revenue by store`, `Bar chart of revenue by category`, `Bar chart of average daily revenue by weekday`.

**2. `build_report(sales_df, folder)`** saves each figure as `folder/<name>.png` (dpi 100) and writes `folder/report.md`:

```text
# Sales report

![<alt text of trend>](trend.png)

![<alt text of stores>](stores.png)
...
```

It returns the list of five `Path`s (the four PNG files in order, then `report.md`) and leaves **no figure open**.

## Example

With the test data the first line of `report.md` is `# Sales report` and it holds four image lines whose alt text is the `alt` of the figure.
