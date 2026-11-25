# Problem plan: da.09 Data visualisation (40 problems)

Rules: [README.md](README.md) (shared, especially R1–R4) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.09.p001`…`p040`, folder `pNNN-slug`.

**Mix:** 12 drill, 14 applied, 10 deep, 4 challenge. **Kinds:** 32 code, 5 trace, 3 explain.
**assessment:** explain = p031, trace = p004, fix = p026, build = p040.
**★ core set (16):** p001, p002, p003, p009, p010, p012, p024, p025, p026, p031, p032, p035, p037, p039, p040, p022.

**Testing notes**
- Every solution function **returns** the `Figure` (or `Axes`/`FacetGrid`/plotly `Figure`); it never calls `plt.show()`.
  Data comes in as a DataFrame argument; tests build small DataFrames inline or with a tiny `make_brewco`-style
  generator in `conftest.py` (§2, keep n ≤ 2,000).
- Test file header: `import matplotlib; matplotlib.use("Agg")` before anything imports pyplot; an autouse fixture
  does `yield; plt.close("all")`.
- Spiked 2026-11-18 (matplotlib 3.x, seaborn, plotly 7.1.0), under the runner's limits: importing matplotlib +
  seaborn + pandas + plotly + scipy and building 6 figures took **3.9 s, 274 MB**. Confirmed readable attributes:
  `len(ax.patches)`, `p.get_height()` / `get_width()`, `ax.get_ylim()`, `ax.get_title()`, `ax.get_ylabel()`,
  `[t.get_text() for t in ax.get_xticklabels()]`, `len(fig.axes)` (a `twinx` adds an Axes), `ax.lines[i].get_xdata()`.
  `sns.barplot` returns an `Axes` whose patches are the **means** and whose `ax.lines` are the error bars (one per bar);
  `sns.relplot` returns a `FacetGrid` (`g.axes.flat`).
- **plotly: test through the figure's properties, not `to_dict()`.** In the installed plotly, `fig.to_dict()["data"][0]["y"]`
  is a compact binary dict (`{'dtype': 'i1', 'bdata': ...}`), not a list. Use `list(fig.data[0].y)`,
  `fig.layout.title.text`, `fig.layout.xaxis.title.text` (the chapter teaches exactly this in §9.5).
- Values read from matplotlib come back as NumPy scalars (`np.float64(5.0)`); compare with `pytest.approx` or `float(...)`.
  Never compare autoscaled limits exactly (5% margins); test `get_ylim()[0] == 0` only when the solution sets it.
- Chapter helpers reused as specs (copy into `conftest.py` when a test needs them, never imported by the solution):
  `describe_fig` (§3.2), `bar_values`, `line_data` (§9.2), `lint_figure` (§9.3), `visual_change` (§6.1),
  `line_angle` (§6.6), `luminance_profile` (§6.9), `rel_luminance`, `contrast_ratio`, `simulate`, `separation` (§8.2),
  `describe_plotly` (§7.2).
- Traces print counts, strings and rounded numbers only (R3), never an Axes repr.

## A. matplotlib anatomy (Ch. 1, 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Figure and Axes ✅ | drill | code | `make_panels(rows, cols, sharey)` → Figure; `len(fig.axes)`; shared y checked with `ax.get_shared_y_axes().joined(a, b)`; figsize honoured |
| 2 | A first labelled bar chart ✅ | drill | code | `bar_chart(categories, values, title, ylabel)`; bar count, heights, title, y label, tick labels in the given order; returns the Figure (message if `None`: "return fig, do not call plt.show()") |
| 3 | Read data back from a figure ✅ | drill | code | write `bar_values(ax)` and `line_data(ax, i)` (§9.2); vertical bars use heights, horizontal bars widths; works on figures the test builds |
| 4 | Anatomy by hand ✅ | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` given code makes a 2×2 grid, 3 lines on one panel, 4 bars on another, a `twinx` on a third; predict printed `len(fig.axes)`, `len(ax.lines)`, `len(ax.patches)` per panel and the titles |
| 5 | Ticks, scales and limits ✅ | applied | code | `revenue_chart(df, log=False)`: linear version has `get_ylim()[0] == 0`; log version `get_yscale() == "log"`; y tick formatter gives `"12,000"` for 12000 (`ax.yaxis.get_major_formatter()(12000, 0)`) |
| 6 | Annotate the peak ✅ | applied | code | `annotate_peak(ax, x, y)` adds one annotation with the max value and a horizontal mean line; tests `ax.texts` contains the formatted max, one `Line2D` with constant y equal to the mean |
| 7 | Size and resolution ✅ | drill | code | `save_png(fig, path, dpi)` to `tmp_path`; read back with `matplotlib.image.imread`: pixel shape = figsize × dpi; PNG magic bytes; also writes SVG when the suffix is `.svg` |
| 8 | Leave no figures open ✅ | deep | code | `render_all(frames, folder)` saves one chart per frame and returns paths; afterwards `plt.get_fignums() == []` (message: "each `plt.subplots()` keeps a figure alive until you close it; 200 of them fill memory") |

## B. Choosing the right chart (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Sorted bars that start at zero ✅ | applied | code | `category_bars(df, cat, val)` horizontal, largest at the top, x axis from 0; reads order via `bar_values` |
| 10 | Monthly line with honest gaps ✅ | applied | code | `monthly_line(df)`: missing months become NaN (a gap), not a straight line across; x covers every month in the range; test checks NaN positions in `get_ydata()` |
| 11 | Histogram counts by hand ✅ | drill | trace | `⚠ HAND-TRACE` 12 inline values, `bins=[0, 10, 20, 30, 40]`; code prints `counts.astype(int).tolist()` from `ax.hist` and which bin the edge value 20 falls in (right-closed last bin rule) |
| 12 | Box-plot statistics ✅ | applied | code | `box_stats(x)` → q1, median, q3, whisker low/high, outliers with the 1.5 × IQR rule; compared with `matplotlib.cbook.boxplot_stats(x)[0]` |
| 13 | ECDF by hand ✅ | drill | trace | `⚠ HAND-TRACE` the chapter's ECDF code on `[3, 1, 2, 2, 5]`; predict the printed `(x, y)` pairs with `y` as fractions `i/n` (`:.1f`) and where the tie at 2 makes a jump of 0.4 |
| 14 | Scatter that survives overplotting ✅ | applied | code | `scatter(df)`: for n > 2,000 uses alpha ≤ 0.3 and size ≤ 10; offsets count = n; axes labelled with units |
| 15 | Stacked bars of shares ✅ | applied | code | `share_bars(df, group, part, value)` 100% stacked; per x position heights sum to 100 (± 1e-9); legend order equals stack order |
| 16 | Diverging Likert bars ✅ | deep | code | §4.6: negatives left of zero, neutral split half on each side; read each bar's `get_x()` and `get_width()`; a 0-count category draws a zero-width bar, not nothing |
| 17 | Annotated heatmap ✅ | applied | code | `heatmap(pivot)` with a colorbar (`len(fig.axes) == 2`) and one text per cell matching the rounded values; NaN cells get no text |
| 18 | Error bars from intervals ✅ | deep | code | `means_with_ci(df, group, value)` uses `mean_ci` (§4.8, given in problem.md); drawn error-bar half-lengths equal the CI half-widths (read from `ax.containers[0]`) |
| 19 | Which chart answers the question? ✅ | drill | explain | 8 questions (compare, trend, distribution, relationship, part-to-whole, survey, matrix, uncertainty) → chart and the reason; answer.md follows the §4.9 chooser |

## C. seaborn (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | What does barplot draw? ✅ | drill | trace | `⚠ HAND-TRACE` 6-row inline DataFrame, `sns.barplot(..., errorbar=None)`; print `[round(float(p.get_height()), 2) for p in ax.patches]` (means, category order = first appearance) |
| 21 | Distributions by group ✅ | applied | code | `hist_by_group(df)` with `hue`, `stat="density"`, `common_norm=False`; for each group the bar areas sum to 1 (± 0.01); legend labels = groups |
| 22 | Facets with relplot ✅ | drill | code | returns a `FacetGrid`; one panel per store; titles are just the store names (`set_titles("{col_name}")`); y shared |
| 23 | Regression line drawn by seaborn ✅ | deep | code | `trend(df)` with `sns.regplot(ci=None)`; slope of the drawn line (from its x/y data) equals `np.polyfit(x, y, 1)[0]` within 1e-6 |
| 24 | Themes without side effects ✅ | deep | code | `themed_chart(df)` uses `with sns.axes_style("whitegrid"):` and `sns.plotting_context` as context managers; test snapshots `mpl.rcParams` before and after: unchanged (message: "`sns.set_theme()` changes every later chart in the program") |

## D. Misleading charts (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Detect a truncated axis ✅ | applied | code | `visual_change(ax)` (§6.1): ratio of drawn bar heights against the true ratio; `is_truncated(ax)` True when a bar chart's y axis does not include 0 |
| 26 | Fix the misleading revenue chart ✅ | deep | code | `assessment = "fix"`; given `revenue_chart(df)` with a truncated y axis, a cherry-picked last-3-months window and an unlabelled unit; fix it. Tests: y starts at 0, x covers the whole date range of `df`, y label contains the unit, title states the change in numbers that match the data |
| 27 | Where do the two axes cross? ✅ | deep | trace | `⚠ HAND-TRACE` the chapter's `dual_axis`/`first_crossing` (§6.2) with two given pairs of limits; predict the printed crossing month; shows that the "crossing" is chosen by the limits, not the data |
| 28 | Bubbles: area, not radius ✅ | applied | code | `bubble_sizes(values, max_area)`: marker size `s` (points²) proportional to the value; doubling a value doubles `s`; the scatter's `get_sizes()` checked |
| 29 | Aspect ratio and slope ✅ | deep | explain | the same series drawn 10:1 and 1:2 (§6.6): what changes and how to choose; checklist: "banking to 45°", "the slope is a drawing choice", "state the scale", "compare panels on the same scale" |
| 30 | Colour maps that deceive ✅ | deep | code | `is_monotone_lightness(cmap_name)` using `luminance_profile` (§6.9): True for viridis and cividis, False for jet and rainbow; `pick_sequential(names)` returns the first honest one |
| 31 | Honest or misleading? ✅ | applied | explain | `assessment = "explain"`; review five described charts (truncated bar, dual axis, pie with 9 slices, 3D bars, cherry-picked window) against the §6.10 checklist: what each makes the reader believe and the fix |

## E. Interactive charts with plotly (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 32 | plotly bars, tested by properties ✅ | drill | code | `px_bars(df)` → `px.bar` horizontal, sorted; tests read `list(fig.data[0].x)`, `fig.layout.title.text`, axis title (message: "do not read `to_dict()`; plotly stores arrays in binary form there") |
| 33 | Hover text and facets ✅ | applied | code | `px_lines(df)` with `hover_data` and `facet_col="store"`; one trace per (store, colour); `customdata` columns in the right order; `hovertemplate` contains the unit |
| 34 | Subplots with graph objects ✅ | challenge | code | `make_subplots(1, 2)` with a `go.Bar` and a `go.Scatter`; second trace on `xaxis == "x2"`; shared y title set once |

## F. Design for the reader (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Contrast ratio ✅ | drill | code | `rel_luminance(hex)`, `contrast_ratio(fg, bg)` (WCAG formula, §8.2); black on white = 21.0; same colour = 1.0; `#777777` on white ≈ 4.48 (just fails AA 4.5) |
| 36 | Colour-blind safe pairs ✅ | deep | code | `safe_pairs(palette, min_sep)` using `simulate`/`separation` (§8.2, given in problem.md and conftest): red/green pair rejected, blue/orange kept |
| 37 | Direct labels instead of a legend ✅ | applied | code | `direct_label(ax)`: no legend afterwards, one text per line at its last point, text colour = line colour |
| 38 | Alt text from the data ✅ | challenge | code | `alt_text(fig)` → `"Bar chart of revenue by store. Highest: Airport (4,210). Lowest: Campus (1,050)."` built from `bar_values`; exact format given; works for horizontal bars too |

## G. Testing charts and the project (Ch. 9–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 39 | A chart linter ✅ | challenge | code | `lint_figure(fig, min_font=8.0, max_legend=7)` (§9.3) → list of problem strings: missing title, unlabelled axis, small font, too many legend entries, truncated bar axis; five bad figures each produce the right message; a good figure → `[]` |
| 40 | A tested visual report ✅ | challenge | code | `assessment = "build"`; `build_report(sales_df, folder)` writes 4 PNG charts and `report.md` (title, alt text per chart) into `tmp_path`; every figure passes the linter (conftest copy); the growth chart's title numbers match the data (§9.4); returns the list of files |

## Counts check

Tiers: drill 12 (1, 2, 3, 4, 7, 11, 13, 19, 20, 22, 32, 35) · applied 14 (5, 6, 9, 10, 12, 14, 15, 17, 21, 25, 28, 31, 33, 37) ·
deep 10 (8, 16, 18, 23, 24, 26, 27, 29, 30, 36) · challenge 4 (34, 38, 39, 40) = 40.
Traces 5: 4, 11, 13, 20, 27. Explain 3: 19, 29, 31. Code 32. One assessment of each kind: explain 31, trace 4, fix 26, build 40.

## Risks and open questions

- seaborn changes defaults between releases (`errorbar` replaced `ci` in 0.12; palette handling of `hue`). Every
  seaborn call in a test or reference passes the argument explicitly (`errorbar=None`, `common_norm=False`).
- matplotlib's `ax.containers` structure for error bars differs between `errorbar` and `bar(yerr=...)`; p18's
  reference must pick one and `problem.md` must say which.
- p36 needs the chapter's colour-blind `simulate` matrix; copy it exactly into `conftest.py` and `problem.md`.
- p7 pixel sizes: `bbox_inches="tight"` changes the size; the problem forbids it or tests only with it off.
