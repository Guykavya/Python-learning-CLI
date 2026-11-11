# Chapter 9 (DA): Data visualisation

A table of 17,000 rows tells you nothing at a glance. A good chart tells you the answer in two seconds: "sales are rising, two stores are lagging, and December is the best month". A bad chart tells you something false in two seconds, and nobody checks, because it *looks* convincing. Visualisation is therefore two skills in one: **drawing** (making the chart appear) and **judging** (deciding which chart to draw and making sure it cannot mislead). The code for a chart takes five lines. The judgement is what this chapter is about.

By the end of this chapter you reach one outcome: **you can pick a chart that answers the question, and label it so that it cannot mislead**. On the way you learn three libraries: **matplotlib**, the foundation that draws everything; **seaborn**, which adds statistical plots on top of it; and **plotly**, which makes interactive charts for the browser.

Prerequisites: da.04 (pandas groupby, reshaping, time series) and the statistical habits of da.08 (uncertainty belongs on a chart; a mean without its interval is incomplete). We use both constantly.

> **Offline rule for this chapter.** matplotlib, seaborn and plotly are installed in the course environment. No internet is needed (plotly's JavaScript is embedded into the HTML files we write). Every dataset is **synthetic**, built in code with seeded random numbers, so you get the same numbers I did. The coffee chain, its stores and its customers are invented.
>
> **How to see the charts.** This chapter is read in a text terminal, so it cannot show pictures. Instead, every chart is drawn in memory and saved as a PNG file in a temporary folder, and the output blocks print what the chart contains: its title, labels, limits and the number of marks. Run the code yourself and open the PNG (or call `plt.show()` in a notebook) to see it. The printed description is not a second-best: it is how you will *test* your own charts in section 9. The same technique makes the exercises of this module checkable by a program. Every output block was produced by running the code above it, in one session from top to bottom. **Versions, file sizes in kilobytes and temporary paths are machine-specific.**

```python run
import sys, os, pathlib, tempfile, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                         # draw into memory/files: no window needed
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objects as go

print("python    ", sys.version.split()[0])
print("matplotlib", matplotlib.__version__)
print("seaborn   ", sns.__version__)
print("plotly    ", plotly.__version__)
print("backend   ", matplotlib.get_backend())
```
```text
python     3.14.4
matplotlib 3.11.2
seaborn    0.13.2
plotly     7.1.0
backend    Agg
```

Two setup lines: compact tables, and a temporary folder where every file is written.

```python run
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 12)
pd.set_option("display.float_format", "{:,.2f}".format)
_tmp = tempfile.TemporaryDirectory()
tmp = pathlib.Path(_tmp.name)
print("temp folder ready:", tmp.exists())
```
```text
temp folder ready: True
```

## Table of contents

1. [What a chart is made of](#1-what-a-chart-is-made-of)
2. [The data: BrewCo](#2-the-data-brewco)
3. [matplotlib anatomy](#3-matplotlib-anatomy)
4. [Choosing the right chart](#4-choosing-the-right-chart)
5. [seaborn: statistical plots](#5-seaborn-statistical-plots)
6. [Misleading charts](#6-misleading-charts)
7. [Interactive charts with plotly](#7-interactive-charts-with-plotly)
8. [Design for the reader](#8-design-for-the-reader)
9. [Testing your charts](#9-testing-your-charts)
10. [Project: a visual report](#10-project-a-visual-report)
11. [Common traps](#11-common-traps)
12. [Summary](#12-summary)

## 1. What a chart is made of

### 1.1 Data, marks and encodings

Every chart does one thing: it turns numbers into **marks** (points, lines, bars, areas) and gives each mark **visual properties** that carry the data. The properties are called **encodings**: horizontal position, vertical position, length, area, colour, shape. A scatter plot encodes one variable in x-position and another in y-position. Add colour for a third. Add size for a fourth. You are mapping *columns* of your table onto *visual channels*.

| Channel | Good for | Accuracy |
|---|---|---|
| Position along a common scale | numbers | the **most accurate** channel |
| Length (bars from a common baseline) | numbers | very accurate |
| Angle, slope | proportions, trends | medium |
| Area | rough magnitude | weak: people under-judge areas |
| Colour **lightness / saturation** | ordered values | weak: only 5-7 levels are distinguishable |
| Colour **hue** | categories | good for 3-7 categories, not numbers |
| Shape | categories | weak beyond 3-4 shapes |

This ordering (studied by Cleveland and McGill in the 1980s) is the single most useful fact in the chapter. When you want a reader to compare two numbers precisely, put them on **position or length**. A pie chart encodes numbers as angles and areas, the weak channels, and that is why bars beat pies for almost every comparison.

### 1.2 The questions behind charts

Choose a chart by the **question** it must answer, not by what looks nice.

| The question | The shape of the answer | Typical chart |
|---|---|---|
| How does a quantity **change over time**? | a trend | line |
| How do **categories compare**? | a ranking or gap | bar (sorted), dot plot |
| How is a quantity **distributed**? | spread, skew, outliers | histogram, box, violin, ECDF |
| How are **two quantities related**? | a pattern between them | scatter, hexbin |
| What are the **parts of a whole**? | shares | stacked bar, 100% bar |
| How much does it **deviate** from a reference? | above / below | diverging bar |
| How do many variables **correlate**? | a matrix | heatmap |
| How **uncertain** is the estimate? | an interval | error bars, bands |

Section 4 draws each of them. A good habit before every chart: write the question in one sentence, then the answer you expect to see. If you cannot, you are not ready to draw.

### 1.3 Three rules that never change

1. **A chart must be readable without you.** Title, axis labels with units, a legend only when needed, a source.
2. **Honest scales.** Bars start at zero. Both axes are labelled. Panels that are compared share a scale.
3. **Show the data and its uncertainty.** Not only the mean; the spread and the sample size when they matter (da.08).

## 2. The data: BrewCo

Our synthetic company, **BrewCo**, is a coffee chain with six stores. We have two years of daily sales (2023 and 2024) by store and product category, plus a customer table and a small satisfaction survey. The generator is long; read the comments, which list the facts hidden in the data that the charts should reveal.

```python run
STORES = {"Harbour": 1.3, "Old Town": 1.0, "Campus": 0.9, "Airport": 1.5, "Mall": 1.2, "Riverside": 0.8}      # relative size
CATS = {"espresso": (3.2, 90), "tea": (2.6, 45), "pastry": (3.8, 60), "cold": (4.1, 40)}                        # (price, base daily units)


def make_brewco(seed=12):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    t, doy, dow = np.arange(len(dates)), dates.day_of_year.to_numpy(), dates.day_of_week.to_numpy()
    temp = (18 - 9 * np.cos(2 * np.pi * (doy - 15) / 365) + rng.normal(0, 2.5, len(dates))).round(1)   # seasonal temperature, C
    growth = 1 + 0.12 * t / 365                                                                           # 12% growth per year
    parts = []
    for s, size in STORES.items():
        promo = np.zeros(len(dates), bool)
        promo[rng.choice(len(dates), 50, replace=False)] = True                                           # about 50 promotion days a year
        weekend = np.where(dow >= 5, 1.25 if s in ("Mall", "Harbour") else 0.8 if s == "Campus" else 1.0, 1.0)
        for c, (price, base) in CATS.items():
            season = (1 + 0.5 * (temp - 18) / 10) if c == "cold" else (1 - 0.12 * (temp - 18) / 10)      # cold drinks follow the heat
            lam = base * size * growth * weekend * np.clip(season, .3, None) * np.where(promo, 1.2, 1)
            units = rng.poisson(lam)
            parts.append(pd.DataFrame({"date": dates, "store": s, "category": c, "units": units,
                                       "revenue": (units * price * np.where(promo, .85, 1)).round(2),
                                       "promo": promo, "temp_c": temp}))
    sales = pd.concat(parts, ignore_index=True)
    closed = (sales["store"] == "Riverside") & (sales["date"] >= "2024-03-01") & (sales["date"] < "2024-03-21")
    sales = sales[~closed].reset_index(drop=True)                                                          # Riverside was closed for 20 days
    # customers: more visits and bigger tickets go with loyalty membership; distance lowers visits
    n = 3000
    age = np.clip(rng.normal(36, 12, n), 16, 80).round()
    dist = rng.exponential(3.0, n).round(1)
    visits = np.clip(rng.gamma(3, 2.2, n) * np.exp(-0.06 * dist), 0.2, None)
    ticket = 5 + 0.04 * age + rng.normal(0, 1.2, n)
    loyal = rng.random(n) < 1 / (1 + np.exp(-(visits - 5) * .5))
    customers = pd.DataFrame({"age": age, "distance_km": dist, "visits_per_month": visits.round(1),
                              "avg_ticket": (ticket + 0.6 * loyal).round(2), "loyal": loyal})
    # satisfaction survey: 1 (very poor) to 5 (excellent); Airport is worse, Campus better
    mood = {"Harbour": 0.0, "Old Town": 0.2, "Campus": 0.6, "Airport": -0.7, "Mall": -0.2, "Riverside": 0.1}
    rows = []
    for s, m in mood.items():
        raw = rng.normal(3.6 + m, 1.0, 300)
        rows.append(pd.DataFrame({"store": s, "rating": np.clip(raw.round(), 1, 5).astype(int)}))
    return sales, customers, pd.concat(rows, ignore_index=True)


sales, customers, survey = make_brewco()
print("sales    ", sales.shape, "| grain: one row per date, store and category")
print("customers", customers.shape, "| grain: one row per customer")
print("survey   ", survey.shape, "| grain: one row per survey answer")
print(sales.head(4).to_string(index=False))
```
```text
sales     (17464, 7) | grain: one row per date, store and category
customers (3000, 5) | grain: one row per customer
survey    (1800, 2) | grain: one row per survey answer
      date   store category  units  revenue  promo  temp_c
2023-01-01 Harbour espresso    162   518.40  False    9.20
2023-01-02 Harbour espresso    139   444.80  False   11.80
2023-01-03 Harbour espresso    148   402.56   True   11.00
2023-01-04 Harbour espresso    114   364.80  False   11.00
```

Before any chart, the habit of every previous chapter: state the grain, and check the data. `sales` has one row per date, store and category. A line chart of "revenue over time" must therefore **sum** the rows first. If you plot the raw rows, matplotlib draws a zig-zag through 17,000 points and the line means nothing.

```python run
print("total revenue :", f"{sales['revenue'].sum():,.0f}")
print("days covered  :", sales["date"].nunique(), "| stores:", sales["store"].nunique(), "| categories:", sales["category"].nunique())
per_store_days = sales.groupby("store")["date"].nunique()
print("days with data per store:", per_store_days.to_dict())
```
```text
total revenue : 4,451,862
days covered  : 731 | stores: 6 | categories: 4
days with data per store: {'Airport': 731, 'Campus': 731, 'Harbour': 731, 'Mall': 731, 'Old Town': 731, 'Riverside': 711}
```

Riverside has 20 fewer days than the others: the store was closed in March 2024. A chart must not hide that. A line that is drawn straight across the missing days implies sales that did not exist; section 6 returns to it.

## 3. matplotlib anatomy

### 3.1 Figure, Axes, Axis, Artists

matplotlib draws everything as a tree of objects, and knowing the tree removes most of the mystery.

| Object | What it is |
|---|---|
| **Figure** | the whole picture: the canvas, its size in inches, the resolution |
| **Axes** | one plot inside the figure: a coordinate system with a title and labels (the name is confusing: *one* Axes is *one* plot) |
| **Axis** | the x-axis or y-axis of an Axes: ticks, tick labels, scale |
| **Artist** | everything you can see: lines, bars (rectangles), text, legends. All of the above are artists |

There are two ways to use the library. The **pyplot** style (`plt.plot(...)`) keeps a hidden "current figure" and "current axes", and is quick in a notebook. The **object-oriented** style makes the objects explicit:

```python run
fig, ax = plt.subplots(figsize=(8, 4))               # one Figure containing one Axes
print(type(fig).__name__, "contains", len(fig.axes), "axes:", type(ax).__name__)
print("the axes have two Axis objects:", type(ax.xaxis).__name__, "and", type(ax.yaxis).__name__)
plt.close(fig)
```
```text
Figure contains 1 axes: Axes
the axes have two Axis objects: XAxis and YAxis
```

Use the object-oriented style in all real work. It makes it clear *which* axes you are drawing on, which is essential once a figure has several. It also lets a function **return** the figure, so that a test can inspect it (section 9).

### 3.2 A first chart, step by step

The question: *how did monthly revenue change over the two years?* The grain of the plotted data must be one row per month, so we aggregate first.

```python run
monthly = sales.groupby(sales["date"].dt.to_period("M").dt.to_timestamp())["revenue"].sum()
print(monthly.head(3).round(0).to_string())
print("months:", len(monthly), "| first:", monthly.index[0].date(), "| last:", monthly.index[-1].date())
```
```text
date
2023-01-01   169,003.00
2023-02-01   154,675.00
2023-03-01   172,143.00
months: 24 | first: 2023-01-01 | last: 2024-12-01
```

Before drawing, decide what the chart should *say*. A first guess: "revenue peaks in summer, because of cold drinks". An analyst who writes that title without checking has made an assertion about the data. Check it first.

```python run
by_month = monthly.groupby(monthly.index.month).mean() / 1000
yearly = monthly.groupby(monthly.index.year).sum()
print("average monthly revenue by calendar month (thousands):", by_month.round(0).astype(int).tolist())
print("highest calendar month:", int(by_month.idxmax()), "| lowest:", int(by_month.idxmin()))
print("yearly totals:", yearly.round(0).astype(int).to_dict(), "| growth 2024 vs 2023:", f"{(yearly[2024] / yearly[2023] - 1) * 100:.1f}%")
```
```text
average monthly revenue by calendar month (thousands): [179, 167, 175, 179, 187, 184, 191, 192, 188, 196, 190, 199]
highest calendar month: 12 | lowest: 2
yearly totals: {2023: 2107837, 2024: 2344025} | growth 2024 vs 2023: 11.2%
```

There is no summer peak: December is the highest month and February the lowest, and the main pattern is **growth** (about 11 percent from 2023 to 2024), which lifts the later months of each year. Cold drinks do peak in summer, but espresso and tea fall in the heat, and the total is nearly flat across the seasons. The finding to put in the title is the growth. Now the chart: create the figure, draw the line, then add what a reader needs. First a bare version.

```python run
def describe_fig(fig):
    """Print what a figure contains. We use this instead of looking at the picture, and later in tests."""
    print(f"figure {fig.get_figwidth():g} x {fig.get_figheight():g} inches, {len(fig.axes)} axes")
    for i, ax in enumerate(fig.axes):
        title = ax.get_title() or ax.get_title(loc="left") or ax.get_title(loc="right")
        print(f"  axes[{i}] title={title!r}  xlabel={ax.get_xlabel()!r}  ylabel={ax.get_ylabel()!r}")
        xl, yl = ax.get_xlim(), ax.get_ylim()
        print(f"           xlim=({xl[0]:.5g}, {xl[1]:.5g})  ylim=({yl[0]:.5g}, {yl[1]:.5g})  "
              f"lines={len(ax.lines)} patches={len(ax.patches)} collections={len(ax.collections)} texts={len(ax.texts)}")
        leg = ax.get_legend()
        if leg:
            print("           legend:", [t.get_text() for t in leg.get_texts()])


fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(monthly.index, monthly.values, marker="o", linewidth=2)
ax.set_title("BrewCo monthly revenue, 2023-2024")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (currency units)")
describe_fig(fig)
fig.savefig(tmp / "monthly_basic.png", dpi=100)
plt.close(fig)
```
```text
figure 8 x 4 inches, 1 axes
  axes[0] title='BrewCo monthly revenue, 2023-2024'  xlabel='Month'  ylabel='Revenue (currency units)'
           xlim=(19323, 20093)  ylim=(1.5197e+05, 2.1149e+05)  lines=1 patches=0 collections=0 texts=0
```

The description says what we expect: one axes, one line, a title, two labels. Notice `ylim`: matplotlib picked the limits itself. That is a decision that affects how the chart reads (section 6). Compare with what a careless chart omits: units, a title that states the finding, a readable axis. Improve it.

```python run
fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
ax.plot(monthly.index, monthly.values / 1000, marker="o", linewidth=2, color="#1b6ca8")
ax.set_title(f"Revenue grew {(yearly[2024] / yearly[2023] - 1) * 100:.0f}% from 2023 to 2024", loc="left", fontsize=13, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Monthly revenue (thousands)")
ax.set_ylim(bottom=0)                                                    # a line chart need not start at 0, but here zero is a fair reference
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
ax.grid(axis="y", alpha=.3)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, -0.02, "Source: BrewCo sales table, all stores and categories.", fontsize=8, color="gray")
describe_fig(fig)
fig.savefig(tmp / "monthly_better.png", dpi=100, bbox_inches="tight")
print("saved file size:", round((tmp / "monthly_better.png").stat().st_size / 1024), "KB (machine-specific)")
plt.close(fig)
```
```text
figure 8 x 4 inches, 1 axes
  axes[0] title='Revenue grew 11% from 2023 to 2024'  xlabel=''  ylabel='Monthly revenue (thousands)'
           xlim=(19323, 20093)  ylim=(0, 211.49)  lines=1 patches=0 collections=0 texts=0
saved file size: 34 KB (machine-specific)
```

What changed, and why:

- The title **states the finding**, not the topic ("Revenue grew 11% from 2023 to 2024" rather than "Revenue over time"). Section 8 explains.
- Values are divided by 1000 and the axis says so; thousands separators help reading.
- The date axis uses a smart formatter instead of 24 crowded labels.
- Light gridlines for reading values; the top and right frame lines are removed (they carry no data).
- A source line. A chart that travels (email, slides) loses its context unless it carries it.

The title is built from the data (`yearly`), so it cannot drift away from the numbers: if the data are refreshed next month, the title updates with them. That is a good habit for any title that contains a number.

### 3.3 Size, resolution and file formats

A figure has a size in **inches** (`figsize`) and a resolution in **dots per inch** (`dpi`); the pixel size is their product.

```python run
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot([0, 1], [0, 1])
for dpi in (50, 100, 200):
    path = tmp / f"size_{dpi}.png"
    fig.savefig(path, dpi=dpi)
    h, w = plt.imread(path).shape[:2]
    print(f"dpi {dpi:3d}: {w} x {h} pixels")
for fmt in ("png", "svg", "pdf"):
    fig.savefig(tmp / f"vec.{fmt}")
print({f.suffix: f.stat().st_size for f in sorted(tmp.glob("vec.*"))}, "bytes (machine-specific)")
plt.close(fig)
```
```text
dpi  50: 300 x 150 pixels
dpi 100: 600 x 300 pixels
dpi 200: 1200 x 600 pixels
{'.pdf': 5057, '.png': 14338, '.svg': 11889} bytes (machine-specific)
```

6 by 3 inches at 100 dpi is 600 by 300 pixels. Three practical rules. Use **PNG** (raster, pixels) for the web and slides at 150 to 200 dpi; use **SVG or PDF** (vector, shapes) for printed reports and anything that will be enlarged, because they stay sharp at any size; and design the figure for its *destination*: a slide needs bigger text and fewer details than a report page.

### 3.4 Ticks, scales and limits

Everything on an axis is controllable: where the ticks are (**locators**), how they are written (**formatters**), the range (**limits**) and the scale (linear, log).

```python run
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), layout="constrained")
x = np.array([1, 10, 100, 1000, 10000])
for ax, scale in zip(axes, ["linear", "log"]):
    ax.plot(x, x, marker="o")
    ax.set_xscale(scale)
    ax.set_yscale(scale)
    ax.set_title(f"{scale} scale")
axes[1].xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
fig.canvas.draw()                                                       # needed before reading tick labels
print("linear x tick labels:", [t.get_text() for t in axes[0].get_xticklabels()][:6])
print("log    x ticks:", axes[1].get_xticks()[:6])
plt.close(fig)
```
```text
linear x tick labels: ['−2000', '0', '2000', '4000', '6000', '8000']
log    x ticks: [1.e-01 1.e+00 1.e+01 1.e+02 1.e+03 1.e+04]
```

On a **log scale** equal distances mean equal *ratios* (a factor of ten per step). The straight line on the right means "grows in proportion". Use a log scale when values span orders of magnitude or when ratios matter more than differences; always label it, because many readers assume linear.

Percent and money formats are one line each:

```python run
fig, ax = plt.subplots()
ax.bar(["A", "B"], [0.25, 0.4])
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
fig.canvas.draw()
print([t.get_text() for t in ax.get_yticklabels()])
plt.close(fig)
```
```text
['0%', '5%', '10%', '15%', '20%', '25%', '30%', '35%', '40%', '45%']
```

### 3.5 Several panels

`plt.subplots(rows, cols)` makes a grid. `sharex` / `sharey` give the panels the same scale, which is required whenever the panels are meant to be compared. `plt.subplot_mosaic` lays out panels by a picture of letters.

```python run
cat_month = sales.assign(month=sales["date"].dt.to_period("M").dt.to_timestamp()).groupby(["month", "category"])["revenue"].sum().unstack() / 1000
fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharex=True, sharey=True, layout="constrained")
for ax, cat in zip(axes.flat, cat_month.columns):
    ax.plot(cat_month.index, cat_month[cat])
    ax.set_title(cat)
fig.supylabel("Monthly revenue (thousands)")
describe_fig(fig)
print("same y-limits in all four panels:", len({tuple(np.round(a.get_ylim(), 6)) for a in axes.flat}) == 1)
plt.close(fig)
```
```text
figure 9 x 6 inches, 4 axes
  axes[0] title='cold'  xlabel=''  ylabel=''
           xlim=(19323, 20093)  ylim=(16.631, 84.761)  lines=1 patches=0 collections=0 texts=0
  axes[1] title='espresso'  xlabel=''  ylabel=''
           xlim=(19323, 20093)  ylim=(16.631, 84.761)  lines=1 patches=0 collections=0 texts=0
  axes[2] title='pastry'  xlabel=''  ylabel=''
           xlim=(19323, 20093)  ylim=(16.631, 84.761)  lines=1 patches=0 collections=0 texts=0
  axes[3] title='tea'  xlabel=''  ylabel=''
           xlim=(19323, 20093)  ylim=(16.631, 84.761)  lines=1 patches=0 collections=0 texts=0
same y-limits in all four panels: True
```

This is a **small multiples** chart: the same plot repeated for each category, on the same scales, so the eye compares shapes. The check on the last line shows what `sharey=True` guarantees. If the four panels had their own y-scales, the tiny pastry line would look as large as the big espresso line, and the comparison would be false.

```python run
fig, axd = plt.subplot_mosaic([["trend", "trend"], ["left", "right"]], figsize=(9, 6), layout="constrained")
print(sorted(axd), "-> a dictionary of axes:", {k: type(v).__name__ for k, v in axd.items()})
plt.close(fig)
```
```text
['left', 'right', 'trend'] -> a dictionary of axes: {'trend': 'Axes', 'left': 'Axes', 'right': 'Axes'}
```

### 3.6 Colour

Colour carries meaning, and misusing it is the second most common chart mistake after the axis. Three kinds of palettes, for three kinds of data:

| Data | Palette | Example |
|---|---|---|
| Categories with no order | **qualitative**: distinct hues | store names |
| Ordered numbers, low to high | **sequential**: one hue, light to dark | revenue per day |
| Numbers around a meaningful centre | **diverging**: two hues meeting at a neutral | change from last year, above or below target |

Choose colours that are **safe for colour-blind readers** (about 8 percent of men). The Okabe-Ito palette is the standard choice for categories; matplotlib's `viridis` is a perceptually even sequential map. Avoid `jet` / rainbow maps: they create false bands and are unreadable in greyscale.

```python run
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
print("Okabe-Ito colours:", OKABE_ITO[:4], "...")
print("matplotlib default cycle :", [matplotlib.colors.to_hex(c) for c in plt.rcParams["axes.prop_cycle"].by_key()["color"][:4]], "...")
cm = matplotlib.colormaps["viridis"]
print("viridis at 0.0, 0.5, 1.0:", [matplotlib.colors.to_hex(cm(v)) for v in (0.0, .5, 1.0)])
print("cm(1) is not cm(1.0):", matplotlib.colors.to_hex(cm(1)), "(an integer picks colour number 1 of 256; use floats from 0 to 1)")
print("number of built-in colormaps:", len(matplotlib.colormaps))
```
```text
Okabe-Ito colours: ['#E69F00', '#56B4E9', '#009E73', '#F0E442'] ...
matplotlib default cycle : ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'] ...
viridis at 0.0, 0.5, 1.0: ['#440154', '#21918c', '#fde725']
cm(1) is not cm(1.0): #440256 (an integer picks colour number 1 of 256; use floats from 0 to 1)
number of built-in colormaps: 194
```

A last rule about colour: **be consistent**. If Airport is orange in the first chart, it must be orange in every other chart of the report. Fix the mapping in one dictionary and reuse it:

```python run
STORE_COLOR = dict(zip(STORES, OKABE_ITO[:6]))
print(STORE_COLOR)
```
```text
{'Harbour': '#E69F00', 'Old Town': '#56B4E9', 'Campus': '#009E73', 'Airport': '#F0E442', 'Mall': '#0072B2', 'Riverside': '#D55E00'}
```

### 3.7 Annotations and reference lines

The data rarely speak for themselves. Mark the thing the reader must see: a threshold, an event, the peak.

```python run
daily = sales.groupby("date")["revenue"].sum()
weekly = daily.resample("W").sum().iloc[1:-1] / 1000          # drop the partial first and last week (1 and 2 days)
peak = weekly.idxmax()
fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
ax.plot(weekly.index, weekly.values, color="#1b6ca8", linewidth=1.5)
ax.axhline(weekly.mean(), color="gray", linestyle="--", linewidth=1)
ax.text(weekly.index[1], weekly.mean() * 1.02, f"average {weekly.mean():,.0f}", color="gray", fontsize=9)
ax.axvspan(pd.Timestamp("2024-03-01"), pd.Timestamp("2024-03-21"), color="#D55E00", alpha=.15)
ax.annotate(f"peak week: {weekly.max():,.0f}", xy=(peak, weekly.max()), xytext=(peak, weekly.max() * 1.12),
            arrowprops={"arrowstyle": "->"}, ha="center")
ax.set_ylim(0, weekly.max() * 1.25)
ax.set_title("Weekly revenue, all stores", loc="left")
ax.set_ylabel("Weekly revenue (thousands)")
describe_fig(fig)
print("peak week starts at:", peak.date(), "| average weekly revenue:", round(weekly.mean(), 1))
plt.close(fig)
```
```text
figure 9 x 4 inches, 1 axes
  axes[0] title='Weekly revenue, all stores'  xlabel=''  ylabel='Weekly revenue (thousands)'
           xlim=(19329, 20122)  ylim=(0, 59.385)  lines=2 patches=1 collections=0 texts=2
peak week starts at: 2024-12-22 | average weekly revenue: 42.6
```

`axhline` and `axvspan` draw reference marks, `text` and `annotate` write on the chart (`annotate` can add an arrow). The description counts them: two texts and one shaded patch. Annotate sparingly: every note should answer a question the reader would otherwise ask.

### 3.8 Housekeeping

Three things trip beginners.

1. **Close figures.** Every `plt.subplots()` creates a figure that stays in memory until closed. A loop that draws 500 charts without `plt.close(fig)` will use gigabytes and prints a warning after 20.
2. **Pyplot's hidden state.** `plt.title(...)` applies to the *current* axes, which may not be the one you think. In multi-panel code, call methods on the axes objects.
3. **Backends.** In a script or a server there is no screen. We selected `Agg`, which draws to files. In a notebook the inline backend shows the figure below the cell. Select the backend *before* importing pyplot.

```python run
before = len(plt.get_fignums())
figs = [plt.figure() for _ in range(3)]
print("open figures:", len(plt.get_fignums()) - before)
for f in figs:
    plt.close(f)
print("after closing:", len(plt.get_fignums()) - before)
```
```text
open figures: 3
after closing: 0
```

Finally, `rcParams` and **style sheets** set defaults for a whole session so that every chart follows one house style:

```python run
print("some styles:", sorted(plt.style.available)[:6])
with plt.rc_context({"axes.spines.top": False, "axes.spines.right": False, "font.size": 11, "axes.titleweight": "bold"}):
    fig, ax = plt.subplots()
    print("top spine visible inside the context:", ax.spines["top"].get_visible())
    plt.close(fig)
fig, ax = plt.subplots()
print("top spine visible outside the context:", ax.spines["top"].get_visible())
plt.close(fig)
```
```text
some styles: ['Solarize_Light2', 'bmh', 'classic', 'dark_background', 'fast', 'fivethirtyeight']
top spine visible inside the context: False
top spine visible outside the context: True
```

`rc_context` changes the settings only inside the `with` block. Put your house style in one place and use it for every figure.


## 4. Choosing the right chart

For each question of section 1.2 we draw the matching chart, check that what it shows is what the data say, and note what can go wrong.

### 4.1 Comparing categories: the bar chart

*Which store sells the most?* The marks are bars; the encoding is **length from a common zero baseline**, one of the most accurate channels. Sort the bars by value so that the ranking is visible, and use horizontal bars when the category names are long.

```python run
rev_store = sales.groupby("store")["revenue"].sum().sort_values()
fig, ax = plt.subplots(figsize=(7, 3.5), layout="constrained")
ax.barh(rev_store.index, rev_store.values / 1000, color="#1b6ca8")
ax.bar_label(ax.containers[0], labels=[f"{v / 1000:,.0f}" for v in rev_store.values], padding=3, fontsize=9)
ax.set_xlabel("Revenue, 2023-2024 (thousands)")
ax.set_title("Airport leads; Riverside is the smallest store", loc="left")
ax.set_xlim(0, rev_store.max() / 1000 * 1.12)
ax.spines[["top", "right"]].set_visible(False)
describe_fig(fig)
widths = [p.get_width() for p in ax.patches]
print("bar lengths equal the data:", np.allclose(widths, rev_store.values / 1000))
print("axis starts at zero:", ax.get_xlim()[0] == 0)
plt.close(fig)
```
```text
figure 7 x 3.5 inches, 1 axes
  axes[0] title='Airport leads; Riverside is the smallest store'  xlabel='Revenue, 2023-2024 (thousands)'  ylabel=''
           xlim=(0, 1099.3)  ylim=(-0.69, 5.69)  lines=0 patches=6 collections=0 texts=6
bar lengths equal the data: True
axis starts at zero: True
```

The check lines are the point: we compare what is **drawn** (the widths of the rectangles) against what is **in the data**, and confirm that the axis starts at zero. A bar's length *is* its value, so a bar chart on a truncated axis lies (section 6.1).

But is "Riverside is the smallest" fair? Riverside was closed for 20 days. A total depends on how many days the store was open; a fair comparison uses **revenue per open day**, the same sum-over-count correction as in da.06.

```python run
days_open = sales.groupby("store")["date"].nunique()
per_day = (sales.groupby("store")["revenue"].sum() / days_open).sort_values()
cmp = pd.DataFrame({"total": rev_store, "days open": days_open, "per open day": per_day}).round(0)
cmp["rank by total"] = cmp["total"].rank(ascending=False).astype(int)
cmp["rank per day"] = cmp["per open day"].rank(ascending=False).astype(int)
print(cmp.sort_values("per open day", ascending=False).to_string())
```
```text
               total  days open  per open day  rank by total  rank per day
store                                                                     
Airport   981,525.00        731      1,343.00              1             1
Harbour   910,244.00        731      1,245.00              2             2
Mall      843,757.00        731      1,154.00              3             3
Old Town  654,446.00        731        895.00              4             4
Campus    554,026.00        731        758.00              5             5
Riverside 507,864.00        711        714.00              6             6
```

The ranking does not change here (Riverside has the smallest per-day revenue too), but its gap to the next store is smaller per day than in total. A good chart would state the denominator: "revenue per open day". Whenever your bars are totals over groups with different exposure (days, customers, area), ask whether a rate is the fairer quantity.

> **Predict the output.** If the bars show **averages** (revenue per day) rather than totals, what extra information does a careful chart need that the bar of a total did not? Recall da.08.

<details><summary>Answer</summary>

The uncertainty. A mean is an estimate from 700 or so days; a bar with no interval hides how much it would wobble. Section 4.8 adds error bars. A bar of a *total over all days* has no sampling uncertainty (it is the whole population of days we observed), but a bar of an *average used to compare stores or predict next year* does.

</details>

### 4.2 Change over time: the line chart

*How did each store's weekly revenue move?* Time goes on the x-axis (position, the best channel), the value on y, and a line connects consecutive points to show the trend. Lines imply **continuity**: connect only points that belong to one continuous series.

First, a design problem: six lines at once.

```python run
weekly_store = (sales.set_index("date").groupby("store")["revenue"].resample("W").sum().unstack(0)).iloc[1:-1] / 1000      # complete weeks only
weekly_store.loc["2024-03-03":"2024-03-24", "Riverside"] = np.nan             # the closure weeks: no data, not zero
print(weekly_store.shape, "| missing cells:", int(weekly_store.isna().sum().sum()))
print(weekly_store.loc["2024-02-25":"2024-03-31", "Riverside"].round(1).to_string())
```
```text
(104, 6) | missing cells: 4
date
2024-02-25   5.00
2024-03-03    NaN
2024-03-10    NaN
2024-03-17    NaN
2024-03-24    NaN
2024-03-31   4.90
Freq: W-SUN
```

The first and last weeks of the data are **partial** (1 January 2023 was a Sunday, so the first "week" holds one day; the last holds two), and we dropped them with `.iloc[1:-1]`. Our first draft of this chart kept them, and the lines plunged to nearly zero at both ends: a fake crash made of a one-day week. Partial periods at the edges are the commonest silent error in time-series charts (da.06, da.07). Riverside has partial or missing weeks around the closure. We set the fully closed weeks to `NaN` so that matplotlib **breaks the line** there instead of connecting the last open week to the first one after reopening (which would draw sales that never happened).

```python run
fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")
for store in weekly_store.columns:
    ax.plot(weekly_store.index, weekly_store[store], color=STORE_COLOR[store], linewidth=1.4, label=store)
ax.set_ylabel("Weekly revenue (thousands)")
ax.set_title("Six stores: the lines overlap, so the picture is hard to read", loc="left")
ax.legend(ncol=3, frameon=False)
describe_fig(fig)
line = ax.lines[weekly_store.columns.get_loc("Riverside")]
yd = line.get_ydata()
print("Riverside line contains gaps (NaN):", int(np.isnan(yd).sum()), "weeks")
plt.close(fig)
```
```text
figure 9 x 4.5 inches, 1 axes
  axes[0] title='Six stores: the lines overlap, so the picture is hard to read'  xlabel=''  ylabel='Weekly revenue (thousands)'
           xlim=(19329, 20122)  ylim=(3.9838, 10.898)  lines=6 patches=0 collections=0 texts=0
           legend: ['Airport', 'Campus', 'Harbour', 'Mall', 'Old Town', 'Riverside']
Riverside line contains gaps (NaN): 4 weeks
```

Six overlapping lines are legible only if they separate cleanly; here they cross a lot, and the legend forces the eye to travel back and forth. Two better designs: **direct labels** (write the name at the end of each line) and **small multiples** (one panel per store, same scales). Small multiples win when lines overlap:

```python run
fig, axes = plt.subplots(2, 3, figsize=(10, 5), sharex=True, sharey=True, layout="constrained")
for ax, store in zip(axes.flat, weekly_store.columns):
    ax.plot(weekly_store.index, weekly_store[store], color=STORE_COLOR[store], linewidth=1.3)
    ax.set_title(store, loc="left", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
fig.supylabel("Weekly revenue (thousands)")
describe_fig(fig)
print("all panels share the y-scale:", len({tuple(np.round(a.get_ylim(), 6)) for a in axes.flat}) == 1)
plt.close(fig)
```
```text
figure 10 x 5 inches, 6 axes
  axes[0] title='Airport'  xlabel=''  ylabel=''
           xlim=(19329, 20122)  ylim=(3.9838, 10.898)  lines=1 patches=0 collections=0 texts=0
  axes[1] title='Campus'  xlabel=''  ylabel=''
           xlim=(19329, 20122)  ylim=(3.9838, 10.898)  lines=1 patches=0 collections=0 texts=0
  axes[2] title='Harbour'  xlabel=''  ylabel=''
           xlim=(19329, 20122)  ylim=(3.9838, 10.898)  lines=1 patches=0 collections=0 texts=0
  axes[3] title='Mall'  xlabel=''  ylabel=''
           xlim=(19329, 20122)  ylim=(3.9838, 10.898)  lines=1 patches=0 collections=0 texts=0
  axes[4] title='Old Town'  xlabel=''  ylabel=''
           xlim=(19329, 20122)  ylim=(3.9838, 10.898)  lines=1 patches=0 collections=0 texts=0
  axes[5] title='Riverside'  xlabel=''  ylabel=''
           xlim=(19329, 20122)  ylim=(3.9838, 10.898)  lines=1 patches=0 collections=0 texts=0
all panels share the y-scale: True
```

Weekly data are noisy. A **moving average** reveals the trend, but it also hides detail, so show both or say which one you plotted:

```python run
daily_total = sales.groupby("date")["revenue"].sum() / 1000
ma7 = daily_total.rolling(7, center=True).mean()
fig, ax = plt.subplots(figsize=(9, 3.8), layout="constrained")
ax.plot(daily_total.index, daily_total.values, color="#9ecae1", linewidth=.8, label="daily")
ax.plot(ma7.index, ma7.values, color="#08519c", linewidth=2, label="7-day average")
ax.set_ylabel("Revenue (thousands)")
ax.legend(frameon=False, loc="upper left")
ax.set_title("A 7-day average removes the weekday cycle", loc="left")
describe_fig(fig)
wk = daily_total.groupby(daily_total.index.dayofweek).mean()
print("average daily revenue by weekday, Mon..Sun (thousands):", wk.round(2).tolist())
plt.close(fig)
```
```text
figure 9 x 3.8 inches, 1 axes
  axes[0] title='A 7-day average removes the weekday cycle'  xlabel=''  ylabel='Revenue (thousands)'
           xlim=(19322, 20124)  ylim=(4.9869, 7.354)  lines=2 patches=0 collections=0 texts=0
           legend: ['daily', '7-day average']
average daily revenue by weekday, Mon..Sun (thousands): [5.99, 5.95, 5.99, 5.98, 5.99, 6.38, 6.36]
```

The weekday pattern is modest here: Saturday and Sunday are a few percent above the other days (the heatmap in 4.7 quantifies it), and it is what the raw line shows as a faint saw-tooth and what the 7-day average removes. Choose the smoothing to match the question: for "is the business growing?" smooth; for "what happens on Saturdays?" do not.

### 4.3 Distributions: histogram, box plot, ECDF

*How much does a typical customer visit, and how unequal is it?* A distribution chart shows the whole shape: centre, spread, skew and outliers, which a single mean hides. The **histogram** counts values in bins; the choice of bin width changes the picture.

```python run
v = customers["visits_per_month"]
print(f"mean {v.mean():.2f} | median {v.median():.2f} | skewness {v.skew():.2f} | max {v.max():.1f}")
fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), sharey=False, layout="constrained")
for ax, bins in zip(axes, (4, 25, 120)):
    ax.hist(v, bins=bins, color="#56B4E9", edgecolor="white")
    ax.set_title(f"{bins} bins", loc="left")
    ax.set_xlabel("Visits per month")
axes[0].set_ylabel("Customers")
describe_fig(fig)
print("bars drawn per panel:", [len(a.patches) for a in axes])
plt.close(fig)
```
```text
mean 5.55 | median 4.90 | skewness 1.25 | max 24.0
figure 11 x 3.2 inches, 3 axes
  axes[0] title='4 bins'  xlabel='Visits per month'  ylabel='Customers'
           xlim=(-0.99, 25.19)  ylim=(0, 2058)  lines=0 patches=4 collections=0 texts=0
  axes[1] title='25 bins'  xlabel='Visits per month'  ylabel=''
           xlim=(-0.99, 25.19)  ylim=(0, 455.7)  lines=0 patches=25 collections=0 texts=0
  axes[2] title='120 bins'  xlabel='Visits per month'  ylabel=''
           xlim=(-0.99, 25.19)  ylim=(0, 102.9)  lines=0 patches=120 collections=0 texts=0
bars drawn per panel: [4, 25, 120]
```

With 4 bins the shape is coarse and hides the peak; with 120 bins it is jagged noise. About 20 to 30 bins suit 3,000 values. The distribution is **right-skewed** (the mean is above the median): most customers visit a few times a month and a few visit very often. Two more views of the same data complement the histogram:

- A **box plot** shows the median, the quartiles and the outliers in a compact form: good for comparing several groups side by side.
- An **ECDF** (empirical cumulative distribution) plots, for each value, the share of customers at or below it: no bins, no smoothing, and it lets you read percentiles directly.

```python run
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), layout="constrained")
axes[0].boxplot([customers.loc[customers["loyal"], "visits_per_month"], customers.loc[~customers["loyal"], "visits_per_month"]],
                tick_labels=["loyal", "not loyal"], showfliers=True)
axes[0].set_ylabel("Visits per month")
axes[0].set_title("Box plot by membership", loc="left")
xs = np.sort(v.to_numpy())
axes[1].step(xs, np.arange(1, len(xs) + 1) / len(xs), where="post", color="#0072B2")
axes[1].yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
axes[1].set_xlabel("Visits per month")
axes[1].set_ylabel("Share of customers at or below")
axes[1].set_title("ECDF", loc="left")
describe_fig(fig)
print("median visits (50% point of the ECDF):", round(float(np.quantile(xs, .5)), 1), "| 90th percentile:", round(float(np.quantile(xs, .9)), 1))
print("median visits, loyal vs not:", customers.groupby("loyal")["visits_per_month"].median().round(1).to_dict())
plt.close(fig)
```
```text
figure 10 x 3.4 inches, 2 axes
  axes[0] title='Box plot by membership'  xlabel=''  ylabel='Visits per month'
           xlim=(0.5, 2.5)  ylim=(-0.99, 25.19)  lines=14 patches=0 collections=0 texts=0
  axes[1] title='ECDF'  xlabel='Visits per month'  ylabel='Share of customers at or below'
           xlim=(-0.99, 25.19)  ylim=(-0.04965, 1.05)  lines=1 patches=0 collections=0 texts=0
median visits (50% point of the ECDF): 4.9 | 90th percentile: 10.0
median visits, loyal vs not: {False: 3.4, True: 6.6}
```

The ECDF answers questions such as "what share of customers visit fewer than 5 times a month?" by reading the curve. The box plot shows that loyal members visit far more.

### 4.4 Relationships: the scatter plot

*Do customers who live farther away visit less?* A scatter plot puts one variable on each axis, one mark per row. With 3,000 points, marks overlap (**overplotting**) and hide the density. Fixes: transparency (`alpha`), smaller marks, or **hexbin** (count points per hexagon).

```python run
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharex=True, sharey=True, layout="constrained")
axes[0].scatter(customers["distance_km"], customers["visits_per_month"], s=25, color="#0072B2")
axes[0].set_title("Plain points: dense areas look the same", loc="left", fontsize=10)
axes[1].scatter(customers["distance_km"], customers["visits_per_month"], s=12, alpha=.2, color="#0072B2")
axes[1].set_title("alpha = 0.2: density appears", loc="left", fontsize=10)
hb = axes[2].hexbin(customers["distance_km"], customers["visits_per_month"], gridsize=25, cmap="viridis", mincnt=1)
axes[2].set_title("Hexbin: counts per cell", loc="left", fontsize=10)
fig.colorbar(hb, ax=axes[2], label="customers")
for ax in axes:
    ax.set_xlabel("Distance to nearest store (km)")
axes[0].set_ylabel("Visits per month")
describe_fig(fig)
r = customers["distance_km"].corr(customers["visits_per_month"])
rs = customers["distance_km"].corr(customers["visits_per_month"], method="spearman")
print(f"Pearson r = {r:.2f} | Spearman = {rs:.2f}")
plt.close(fig)
```
```text
figure 12 x 3.6 inches, 4 axes
  axes[0] title='Plain points: dense areas look the same'  xlabel='Distance to nearest store (km)'  ylabel='Visits per month'
           xlim=(-1.205, 25.305)  ylim=(-0.99, 25.19)  lines=0 patches=0 collections=1 texts=0
  axes[1] title='alpha = 0.2: density appears'  xlabel='Distance to nearest store (km)'  ylabel=''
           xlim=(-1.205, 25.305)  ylim=(-0.99, 25.19)  lines=0 patches=0 collections=1 texts=0
  axes[2] title='Hexbin: counts per cell'  xlabel='Distance to nearest store (km)'  ylabel=''
           xlim=(-1.205, 25.305)  ylim=(-0.99, 25.19)  lines=0 patches=0 collections=1 texts=0
  axes[3] title=''  xlabel=''  ylabel='customers'
           xlim=(0, 1)  ylim=(1, 87)  lines=0 patches=0 collections=2 texts=0
Pearson r = -0.25 | Spearman = -0.25
```

The data are the same in all three panels; only the first hides how crowded the lower-left is. Add a fitted line to summarise the trend, and report the strength:

```python run
slope, intercept = np.polyfit(customers["distance_km"], customers["visits_per_month"], 1)
fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
ax.scatter(customers["distance_km"], customers["visits_per_month"], s=10, alpha=.2, color="#0072B2")
xx = np.linspace(0, customers["distance_km"].max(), 50)
ax.plot(xx, slope * xx + intercept, color="#D55E00", linewidth=2, label=f"line: {slope:.2f} visits per km")
ax.set(xlabel="Distance (km)", ylabel="Visits per month", title="Each extra km goes with fewer visits")
ax.legend(frameon=False)
describe_fig(fig)
print(f"slope {slope:.3f}, intercept {intercept:.2f}")
plt.close(fig)
```
```text
figure 6 x 4 inches, 1 axes
  axes[0] title='Each extra km goes with fewer visits'  xlabel='Distance (km)'  ylabel='Visits per month'
           xlim=(-1.205, 25.305)  ylim=(-1.8304, 25.23)  lines=1 patches=0 collections=1 texts=0
           legend: ['line: -0.29 visits per km']
slope -0.291, intercept 6.42
```

The title says "goes with", not "causes": this is an association in observational data (da.08). A straight line is also a modelling choice; the relation here is closer to a decay, and the line understates the drop near the shop and overstates it far away. Charts of relationships invite causal readings; the words in the title must resist them.

### 4.5 Parts of a whole: stacked bars

*What is the product mix of each store?* Stacked bars show composition. Two versions: **absolute** (totals comparable, but only the bottom segment is easy to compare) and **100 percent** (shares comparable, totals hidden).

```python run
mix = sales.groupby(["store", "category"])["revenue"].sum().unstack()
share = mix.div(mix.sum(axis=1), axis=0) * 100
order = share.sort_values("cold").index
CAT_COLOR = dict(zip(CATS, [OKABE_ITO[5], OKABE_ITO[1], OKABE_ITO[0], OKABE_ITO[2]]))
fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
left = np.zeros(len(order))
for cat in share.columns:
    ax.barh(order, share.loc[order, cat], left=left, color=CAT_COLOR[cat], label=cat)
    left += share.loc[order, cat].to_numpy()
ax.set_xlim(0, 100)
ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
ax.set_xlabel("Share of store revenue")
ax.set_title("Every store sells almost the same product mix", loc="left")
ax.legend(ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(.5, -.28))
describe_fig(fig)
print("each bar sums to 100%:", bool(np.allclose(share.sum(axis=1), 100)))
print(share.round(1).loc[order].to_string())
plt.close(fig)
```
```text
figure 8 x 4 inches, 1 axes
  axes[0] title='Every store sells almost the same product mix'  xlabel='Share of store revenue'  ylabel=''
           xlim=(0, 100)  ylim=(-0.69, 5.69)  lines=0 patches=24 collections=0 texts=0
           legend: ['cold', 'espresso', 'pastry', 'tea']
each bar sums to 100%: True
category   cold  espresso  pastry   tea
store                                  
Campus    20.60     36.10   28.60 14.70
Old Town  20.70     36.10   28.60 14.60
Mall      20.70     36.10   28.60 14.60
Harbour   20.80     35.90   28.60 14.80
Airport   20.80     36.10   28.60 14.50
Riverside 20.80     36.10   28.40 14.70
```

The chart's message is **sameness**: the six bars are nearly identical (cold drinks 20.6 to 20.8 percent everywhere). That is a finding, and it is the reason to read the table too: when differences are small, bars hide them and numbers show them. The check "each bar sums to 100 percent" belongs in every composition chart. Comparing the middle segments between bars is hard (they do not share a baseline); if the key message is about one category, plot that category alone as a sorted bar chart. And **avoid pie charts** for more than 2 or 3 slices: angles and areas are the weak channels, and a ring of 6 similar slices cannot be ranked by eye, while the table above gives the answer immediately.

### 4.6 Diverging bars: Likert scores

*How satisfied are customers, per store?* Ratings 1 to 5 have a neutral centre (3). A **diverging** chart puts the negative answers to the left of zero and the positive to the right, so the eye sees the balance at once.

```python run
ct = pd.crosstab(survey["store"], survey["rating"], normalize="index") * 100
net = (ct[[4, 5]].sum(axis=1) - ct[[1, 2]].sum(axis=1)).sort_values()
print(ct.round(0).astype(int).loc[net.index].to_string())
fig, ax = plt.subplots(figsize=(7, 3.6), layout="constrained")
colors = ["#D55E00" if v < 0 else "#0072B2" for v in net]
ax.barh(net.index, net.values, color=colors)
ax.axvline(0, color="black", linewidth=1)
ax.set_xlabel("Net satisfaction: % rating 4-5 minus % rating 1-2")
ax.set_title("Airport customers are the least satisfied", loc="left")
ax.bar_label(ax.containers[0], labels=[f"{v:+.0f}" for v in net.values], padding=3)
describe_fig(fig)
print("negative bars:", int((net < 0).sum()), "| positive bars:", int((net > 0).sum()))
plt.close(fig)
```
```text
rating     1   2   3   4   5
store                       
Airport    8  25  34  26   6
Mall       4  14  34  33  14
Harbour    0  12  31  34  23
Riverside  1  11  31  36  22
Old Town   1   6  31  39  23
Campus     0   2  21  37  40
figure 7 x 3.6 inches, 1 axes
  axes[0] title='Airport customers are the least satisfied'  xlabel='Net satisfaction: % rating 4-5 minus % rating 1-2'  ylabel=''
           xlim=(-5.45, 77.783)  ylim=(-0.69, 5.69)  lines=1 patches=6 collections=0 texts=6
negative bars: 1 | positive bars: 5
```

Two colours meet at a meaningful zero, which is the right use of a diverging scheme. The reader should also be told how many people answered (300 per store here); a satisfaction score from 8 customers deserves less trust than one from 300.

### 4.7 Heatmaps

*When during the week does each category sell?* A heatmap encodes a number as **colour** in a grid. Colour is a weak channel, so a heatmap suits *patterns* (a bright band, a dark block), not exact values; add the numbers when exactness matters.

```python run
dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
hm = sales.assign(dow=sales["date"].dt.day_of_week).groupby(["category", "dow"])["units"].mean().unstack()
hm.columns = dow_names
hm_idx = hm.div(hm.mean(axis=1), axis=0)                    # index: 1.0 = the category's own weekly average
fig, ax = plt.subplots(figsize=(7, 3.4), layout="constrained")
im = ax.imshow(hm_idx.values, cmap="RdBu_r", vmin=0.85, vmax=1.15, aspect="auto")
ax.set_xticks(range(7), dow_names)
ax.set_yticks(range(len(hm_idx)), hm_idx.index)
for i in range(hm_idx.shape[0]):
    for j in range(7):
        ax.text(j, i, f"{hm_idx.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
fig.colorbar(im, ax=ax, label="vs the category's weekly average (1.00)")
ax.set_title("Weekend sales run about 5% above the weekly average, in every category", loc="left", fontsize=11)
describe_fig(fig)
print(hm_idx.round(2).to_string())
print("Saturday/Sunday vs weekday index:", round(float(hm_idx[["Sat", "Sun"]].mean().mean()), 2), "vs", round(float(hm_idx[["Mon", "Tue", "Wed", "Thu", "Fri"]].mean().mean()), 2))
plt.close(fig)
```
```text
figure 7 x 3.4 inches, 2 axes
  axes[0] title='Weekend sales run about 5% above the weekly average, in every category'  xlabel=''  ylabel=''
           xlim=(-0.5, 6.5)  ylim=(3.5, -0.5)  lines=0 patches=0 collections=0 texts=28
  axes[1] title=''  xlabel=''  ylabel="vs the category's weekly average (1.00)"
           xlim=(0, 1)  ylim=(0.85, 1.15)  lines=0 patches=0 collections=2 texts=0
          Mon  Tue  Wed  Thu  Fri  Sat  Sun
category                                   
cold     0.97 0.99 0.99 0.98 0.98 1.05 1.03
espresso 0.99 0.97 0.98 0.98 0.98 1.05 1.05
pastry   0.98 0.98 0.98 0.98 0.99 1.05 1.05
tea      0.99 0.97 0.98 0.98 0.98 1.05 1.05
Saturday/Sunday vs weekday index: 1.05 vs 0.98
```

Two design decisions. The colour map is **diverging** (red above, blue below) with its centre fixed at 1.00 by `vmin`/`vmax`, because the data have a natural centre. Dividing by each category's own average (an *index*) puts espresso (many units) and cold drinks (few) on one scale; the raw units would have shown only that espresso sells more. And the title states the finding; we confirm it with the last print: weekend index above 1, weekday index below 1.

### 4.8 Showing uncertainty

*Do loyalty members spend more per visit?* A bar of two means invites the conclusion "yes, by this much". With error bars (da.08) the reader sees how sure we are. Compute the interval, then draw it.

```python run
from scipy import stats


def mean_ci(x, level=0.95):
    x = np.asarray(x, float)
    se = x.std(ddof=1) / np.sqrt(len(x))
    h = stats.t.ppf((1 + level) / 2, len(x) - 1) * se
    return x.mean(), h


rows = []
for name, g in customers.groupby("loyal"):
    m, h = mean_ci(g["avg_ticket"])
    rows.append({"group": "loyal" if name else "not loyal", "n": len(g), "mean": m, "half_width": h})
ci_tbl = pd.DataFrame(rows)
print(ci_tbl.round(3).to_string(index=False))
fig, ax = plt.subplots(figsize=(5, 4), layout="constrained")
ax.errorbar(ci_tbl["group"], ci_tbl["mean"], yerr=ci_tbl["half_width"], fmt="o", capsize=6, color="#0072B2", markersize=8)
ax.set_ylim(0, ci_tbl["mean"].max() * 1.25)
ax.set_ylabel("Average ticket (currency units)")
ax.set_title("Loyal members spend more per visit (95% CI)", loc="left", fontsize=11)
describe_fig(fig)
diff = ci_tbl["mean"].iloc[1] - ci_tbl["mean"].iloc[0]
print(f"difference {diff:.2f}; the two intervals do not overlap: {ci_tbl['mean'].iloc[0] + ci_tbl['half_width'].iloc[0] < ci_tbl['mean'].iloc[1] - ci_tbl['half_width'].iloc[1]}")
plt.close(fig)
```
```text
    group    n  mean  half_width
not loyal 1405  6.47        0.07
    loyal 1595  7.06        0.06
figure 5 x 4 inches, 1 axes
  axes[0] title='Loyal members spend more per visit (95% CI)'  xlabel=''  ylabel='Average ticket (currency units)'
           xlim=(-0.05, 1.05)  ylim=(0, 8.8227)  lines=3 patches=0 collections=1 texts=0
difference 0.59; the two intervals do not overlap: True
```

A **point with an interval** (a dot plot) is often better than a bar for a mean: the bar's length is meaningless here (a mean ticket of 7 is not "7 units of ticket from zero" in an interesting way), while the position of the dot and the interval around it are what we want to compare. If you use bars, start them at zero and put the interval on top. In the caption, say what the whiskers are (95 percent confidence interval, not a standard deviation).

### 4.9 A chart chooser

| Question | First choice | Alternatives | Avoid |
|---|---|---|---|
| Trend over time | line | area (one series), small multiples | bars for dense time series |
| Compare categories | sorted bar | dot plot | pie, 3D bars |
| Distribution of one variable | histogram, ECDF | box, violin | a bare mean |
| Distribution across groups | box, violin, strip | overlaid ECDFs | many overlapping histograms |
| Relationship of two numbers | scatter (+ alpha or hexbin) | binned means, 2D density | dual-axis lines |
| Share of a whole | 100% stacked bar | single sorted bar | pie with many slices |
| Above / below a reference | diverging bar | lollipop | one colour for both directions |
| Pattern over two categories | heatmap | small multiples | rainbow colour maps |
| Estimate with uncertainty | dot with interval | bar with error bar | bare bars |

## 5. seaborn: statistical plots

### 5.1 What seaborn adds

matplotlib draws what you tell it, mark by mark. **seaborn** works one level higher: you give it a tidy DataFrame (one row per observation, one column per variable) and **map columns to encodings**, and it computes the statistics (means, intervals, densities, regression lines) for you. It draws on matplotlib axes, so everything of section 3 still applies.

Two families of functions exist. **Axes-level** functions (`histplot`, `scatterplot`, `barplot`, ...) draw on one matplotlib Axes that you provide with `ax=`. **Figure-level** functions (`displot`, `relplot`, `catplot`, `lmplot`) create the whole figure, and can split the data into rows and columns of panels (`row=`, `col=`) automatically.

```python run
sns.set_theme(style="whitegrid", context="notebook", palette="colorblind")
fig, ax = plt.subplots(figsize=(6, 3.5), layout="constrained")
res = sns.histplot(data=customers, x="avg_ticket", hue="loyal", stat="density", common_norm=False, element="step", bins=30, ax=ax)
print("returned object:", type(res).__name__, "| is the axes we passed:", res is ax)
ax.set_title("Loyal members have bigger tickets", loc="left")
describe_fig(fig)
print("median ticket by membership:", customers.groupby("loyal")["avg_ticket"].median().round(2).to_dict())
plt.close(fig)
```
```text
returned object: Axes | is the axes we passed: True
figure 6 x 3.5 inches, 1 axes
  axes[0] title='Loyal members have bigger tickets'  xlabel='avg_ticket'  ylabel='Density'
           xlim=(2.0665, 12.264)  ylim=(0, 0.38987)  lines=0 patches=0 collections=2 texts=0
           legend: ['False', 'True']
median ticket by membership: {False: 6.45, True: 7.09}
```

`hue="loyal"` splits the data and draws one histogram per group in different colours, adding a legend. `stat="density"` with `common_norm=False` scales each group's histogram to its own area, which makes groups of different size comparable (loyal members are fewer). Keep in mind that this option decides what the chart can and cannot say: with raw counts the larger group would dominate the picture.

### 5.2 Distributions

```python run
fig, axes = plt.subplots(1, 4, figsize=(15, 3.6), layout="constrained")
sns.kdeplot(data=customers, x="age", hue="loyal", fill=True, common_norm=False, ax=axes[0])
sns.ecdfplot(data=customers, x="visits_per_month", hue="loyal", ax=axes[1])
sns.boxplot(data=customers, x="loyal", y="avg_ticket", ax=axes[2])
sns.violinplot(data=customers, x="loyal", y="avg_ticket", inner="quartile", ax=axes[3])
for ax, t in zip(axes, ["KDE (smooth density)", "ECDF", "Box plot", "Violin plot"]):
    ax.set_title(t, loc="left", fontsize=10)
describe_fig(fig)
print("patches per panel (boxes/violins/fills):", [len(a.patches) + len(a.collections) for a in axes])
plt.close(fig)
```
```text
figure 15 x 3.6 inches, 4 axes
  axes[0] title='KDE (smooth density)'  xlabel='age'  ylabel='Density'
           xlim=(4.0074, 91.993)  ylim=(0, 0.035476)  lines=0 patches=0 collections=2 texts=0
           legend: ['False', 'True']
  axes[1] title='ECDF'  xlabel='visits_per_month'  ylabel='Proportion'
           xlim=(-0.99, 25.19)  ylim=(0, 1)  lines=2 patches=0 collections=0 texts=0
           legend: ['False', 'True']
  axes[2] title='Box plot'  xlabel='loyal'  ylabel='avg_ticket'
           xlim=(-0.5, 1.5)  ylim=(2.0665, 12.264)  lines=12 patches=2 collections=0 texts=0
  axes[3] title='Violin plot'  xlabel='loyal'  ylabel='avg_ticket'
           xlim=(-0.5, 1.5)  ylim=(1.4003, 12.906)  lines=6 patches=0 collections=2 texts=0
patches per panel (boxes/violins/fills): [2, 0, 2, 2]
```

The **kernel density estimate** (KDE) smooths a histogram into a curve; it is pretty but can invent mass beyond the data (a smooth tail to negative ages). The **violin plot** draws the KDE mirrored around each category, with the quartiles marked. Strip and swarm plots show every point, best for small samples (under about 200); put them *over* a box plot.

### 5.3 Categories: bars with built-in intervals

`sns.barplot` computes the **mean** of `y` per category and a **95 percent confidence interval by the bootstrap** (da.08), and draws both. This is convenient, and the source of a classic trap: it *aggregates for you*.

```python run
fig, ax = plt.subplots(figsize=(6, 3.5), layout="constrained")
sns.barplot(data=customers.assign(group=np.where(customers["loyal"], "loyal", "not loyal")), x="group", y="avg_ticket",
            errorbar=("ci", 95), n_boot=2000, seed=1, capsize=.15, ax=ax)
ax.set_ylim(0, None)
ax.set_title("Mean ticket with a 95% bootstrap interval", loc="left")
describe_fig(fig)
bar_heights = [round(p.get_height(), 3) for p in ax.patches]
fig.canvas.draw()
labels = [t.get_text() for t in ax.get_xticklabels()]
print("bar heights by label:", dict(zip(labels, [float(h) for h in bar_heights])))
print("manual means         :", {("loyal" if k else "not loyal"): float(v) for k, v in customers.groupby("loyal")["avg_ticket"].mean().round(3).items()})
print("error-bar lines drawn:", len(ax.lines))
plt.close(fig)
```
```text
figure 6 x 3.5 inches, 1 axes
  axes[0] title='Mean ticket with a 95% bootstrap interval'  xlabel='group'  ylabel='avg_ticket'
           xlim=(-0.5, 1.5)  ylim=(0, 7.4711)  lines=2 patches=2 collections=0 texts=0
bar heights by label: {'loyal': 7.058, 'not loyal': 6.471}
manual means         : {'not loyal': 6.471, 'loyal': 7.058}
error-bar lines drawn: 2
```

The bar heights equal our manual means (seaborn orders the bars by first appearance in the data, so check the labels, not the position), and the interval comes from resampling. Whenever a seaborn function *summarises* (means, intervals), **know what it summarises**. The most dangerous case is `lineplot` with several rows per x value:

```python run
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), layout="constrained")
sub = sales[sales["date"] >= "2024-01-01"]
sns.lineplot(data=sub, x="date", y="revenue", ax=axes[0])                      # one row per date, store and category!
axes[0].set_title("lineplot on raw rows: what is this?", loc="left", fontsize=10)
tot = sub.groupby("date", as_index=False)["revenue"].sum()
sns.lineplot(data=tot, x="date", y="revenue", ax=axes[1])
axes[1].set_title("aggregated first: daily total", loc="left", fontsize=10)
fig.canvas.draw()
y0 = axes[0].lines[0].get_ydata()
y1 = axes[1].lines[0].get_ydata()
print(f"left panel line: values around {np.nanmean(y0):,.0f} (the MEAN revenue of a store-category-day row)")
print(f"right panel line: values around {np.nanmean(y1):,.0f} (the TOTAL revenue of a day)")
print("rows per date in the raw table:", int(sub.groupby('date').size().median()))
plt.close(fig)
```
```text
left panel line: values around 269 (the MEAN revenue of a store-category-day row)
right panel line: values around 6,404 (the TOTAL revenue of a day)
rows per date in the raw table: 24
```

The left chart is a perfectly valid mean-per-row with a confidence band, but a reader will take it for daily revenue, and it is 24 times smaller. This is the **grain** lesson of da.06 for charts: before you plot, say what one row is, and aggregate to the grain the title promises.

### 5.4 Relationships and regression

```python run
fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), layout="constrained")
smp = customers.sample(800, random_state=3)
sns.scatterplot(data=smp, x="age", y="avg_ticket", hue="loyal", alpha=.6, ax=axes[0])
sns.regplot(data=smp, x="age", y="avg_ticket", scatter_kws={"alpha": .25, "s": 12}, line_kws={"color": "#D55E00"}, ci=95, ax=axes[1])
sns.heatmap(customers[["age", "distance_km", "visits_per_month", "avg_ticket"]].corr(), annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=axes[2])
for ax, t in zip(axes, ["scatter + hue", "regression with 95% band", "correlation matrix"]):
    ax.set_title(t, loc="left", fontsize=10)
describe_fig(fig)
cm_ = customers[["age", "distance_km", "visits_per_month", "avg_ticket"]].corr()
print("age vs ticket r =", round(cm_.loc["age", "avg_ticket"], 2), "| distance vs visits r =", round(cm_.loc["distance_km", "visits_per_month"], 2))
plt.close(fig)
```
```text
figure 14 x 3.8 inches, 4 axes
  axes[0] title='scatter + hue'  xlabel='age'  ylabel='avg_ticket'
           xlim=(12.85, 82.15)  ylim=(2.35, 11.81)  lines=2 patches=0 collections=1 texts=0
           legend: ['False', 'True']
  axes[1] title='regression with 95% band'  xlabel='age'  ylabel='avg_ticket'
           xlim=(12.85, 82.15)  ylim=(2.35, 11.81)  lines=1 patches=0 collections=2 texts=0
  axes[2] title='correlation matrix'  xlabel=''  ylabel=''
           xlim=(0, 4)  ylim=(4, 0)  lines=0 patches=0 collections=1 texts=16
  axes[3] title=''  xlabel=''  ylabel=''
           xlim=(0, 1)  ylim=(-1, 1)  lines=0 patches=0 collections=2 texts=0
age vs ticket r = 0.36 | distance vs visits r = -0.25
```

`regplot` draws the least-squares line **and a confidence band** for the line (bootstrapped), the uncertainty of da.08 made visible: the band is narrow where there are many points and fans out at the edges. The correlation heatmap uses a diverging map centred on zero with fixed limits of -1 and 1, so colours mean the same thing on every chart. Annotate the cells: a heatmap of correlations without numbers is a decoration.

### 5.5 Figure-level functions and facets

`relplot`, `catplot` and `displot` create the figure and can split it into **facets**. They return a `FacetGrid` (a wrapper around the figure).

```python run
by_week = (sales.assign(week=sales["date"].dt.to_period("W").dt.start_time)
                .groupby(["week", "store", "category"], as_index=False)["revenue"].sum())
g = sns.relplot(data=by_week, x="week", y="revenue", hue="category", col="store", col_wrap=3, kind="line",
                height=2.2, aspect=1.5, errorbar=None, facet_kws={"sharey": True})
g.set_titles("{col_name}")
g.set_axis_labels("", "Weekly revenue")
print(type(g).__name__, "| panels:", len(g.axes.flat), "| figure size:", g.fig.get_size_inches().round(1).tolist())
describe_fig(g.fig)
plt.close(g.fig)
```
```text
FacetGrid | panels: 6 | figure size: [11.1, 4.4]
figure 11.1167 x 4.4 inches, 6 axes
  axes[0] title='Airport'  xlabel=''  ylabel='Weekly revenue'
           xlim=(19315, 20124)  ylim=(-168.14, 4523.2)  lines=8 patches=0 collections=0 texts=0
  axes[1] title='Campus'  xlabel=''  ylabel=''
           xlim=(19315, 20124)  ylim=(-168.14, 4523.2)  lines=4 patches=0 collections=0 texts=0
  axes[2] title='Harbour'  xlabel=''  ylabel=''
           xlim=(19315, 20124)  ylim=(-168.14, 4523.2)  lines=4 patches=0 collections=0 texts=0
  axes[3] title='Mall'  xlabel=''  ylabel='Weekly revenue'
           xlim=(19315, 20124)  ylim=(-168.14, 4523.2)  lines=4 patches=0 collections=0 texts=0
  axes[4] title='Old Town'  xlabel=''  ylabel=''
           xlim=(19315, 20124)  ylim=(-168.14, 4523.2)  lines=4 patches=0 collections=0 texts=0
  axes[5] title='Riverside'  xlabel=''  ylabel=''
           xlim=(19315, 20124)  ylim=(-168.14, 4523.2)  lines=4 patches=0 collections=0 texts=0
```

One call gave six panels (one per store), four lines each (one per category), a shared y-scale, and a legend. Writing it by hand would take thirty lines. The price is less control: when you need exact layout, use matplotlib directly, or retrieve the axes (`g.axes`) and adjust.

```python run
g = sns.catplot(data=customers.assign(group=np.where(customers["loyal"], "loyal", "not loyal")), x="group", y="visits_per_month",
                kind="box", col=pd.cut(customers["age"], [15, 30, 45, 90], labels=["under 30", "30-44", "45+"]), height=3, aspect=.8)
g.set_axis_labels("", "Visits per month")
print("panels:", len(g.axes.flat), [ax.get_title() for ax in g.axes.flat])
plt.close(g.fig)
```
```text
panels: 3 ['age = under 30', 'age = 30-44', 'age = 45+']
```

### 5.6 Themes, palettes and contexts

`sns.set_theme(style=..., context=..., palette=...)` sets the look for everything after it. `style` is the background and grid (`whitegrid`, `ticks`, `dark`); `context` scales the text (`paper`, `notebook`, `talk`, `poster`), so one script can produce a figure for a report or a slide; `palette` sets the colours. Seaborn's `"colorblind"` palette is a good default.

```python run
for ctx in ("paper", "notebook", "talk", "poster"):
    with sns.plotting_context(ctx):
        print(f"{ctx:9} font size {plt.rcParams['font.size']:4.1f}, line width {plt.rcParams['lines.linewidth']:.2f}")
print("colorblind palette:", sns.color_palette("colorblind").as_hex()[:4], "...")
print("sequential 'rocket' (5 steps):", sns.color_palette("rocket", 5).as_hex())
print("diverging 'vlag' (5 steps)   :", sns.color_palette("vlag", 5).as_hex())
```
```text
paper     font size  9.6, line width 1.20
notebook  font size 12.0, line width 1.50
talk      font size 18.0, line width 2.25
poster    font size 24.0, line width 3.00
colorblind palette: ['#0173b2', '#de8f05', '#029e73', '#d55e00'] ...
sequential 'rocket' (5 steps): ['#3f1b43', '#841e5a', '#cb1b4f', '#f06043', '#f6ab83']
diverging 'vlag' (5 steps)   : ['#7896c1', '#bdc6d7', '#faf5f4', '#e1b9b6', '#c67875']
```

### 5.7 seaborn or matplotlib?

| Situation | Use |
|---|---|
| quick statistical views of a tidy table (distribution by group, regression, correlation matrix) | seaborn |
| facets by one or two categorical columns | seaborn figure-level |
| exact control of layout, annotations, custom marks | matplotlib |
| a chart you must test or embed in a layout | build with matplotlib (or seaborn axes-level) and return the `Figure` |

They combine: draw with seaborn on an axes, then refine with matplotlib methods (`ax.set_title`, `ax.annotate`). That is how we keep both the convenience and the control.


## 6. Misleading charts

Most misleading charts are not made by liars. They are made by people who accepted a default, or who wanted a more dramatic picture, or who did not check what the chart implies. The reader trusts the picture first and the numbers second. Your job is to make sure the picture does not claim more than the numbers do.

Tufte's idea of the **lie factor** makes this measurable: the size of the effect *shown in the graphic* divided by the size of the effect *in the data*. A honest chart has a lie factor of 1.

```text
lie factor = (visual change, as a share of the first value) / (data change, as a share of the first value)
```

### 6.1 The truncated bar axis

Compare revenue of 2023 and 2024 (a growth of 11 percent). The same two bars, drawn with two different y-axis limits:

```python run
yr = sales.groupby(sales["date"].dt.year)["revenue"].sum() / 1e6
print("revenue (millions):", yr.round(3).to_dict(), "| data change:", f"{(yr[2024] / yr[2023] - 1) * 100:.1f}%")


def visual_change(ax):
    """The change between the first and second bar as the eye sees it: heights measured from the axis bottom."""
    y0 = ax.get_ylim()[0]
    h = [p.get_height() - y0 for p in ax.patches]
    return h[1] / h[0] - 1


fig, axes = plt.subplots(1, 2, figsize=(8, 3.6), layout="constrained")
for ax, bottom in zip(axes, (None, 2.0)):
    ax.bar(["2023", "2024"], yr.values, color="#1b6ca8")
    ax.set_ylim(bottom=bottom if bottom is not None else 0)
    ax.set_ylabel("Revenue (millions)")
    ax.set_title("axis from 0" if bottom is None else f"axis from {bottom}", loc="left", fontsize=10)
data_change = yr[2024] / yr[2023] - 1
for ax, name in zip(axes, ("honest", "truncated")):
    vc = visual_change(ax)
    print(f"{name:10} visual change {vc * 100:6.1f}%  | lie factor {vc / data_change:5.2f}")
plt.close(fig)
```
```text
revenue (millions): {2023: 2.108, 2024: 2.344} | data change: 11.2%
honest     visual change   11.2%  | lie factor  1.00
truncated  visual change  219.0%  | lie factor 19.55
```

On the truncated axis the second bar looks more than **three times** as tall as the first (219 percent taller), for a growth of 11 percent: a lie factor near 20. A bar's *length* is the data. If you cut the bottom off, you cut off the data. **Bars start at zero**, no exception. For a line chart, the axis need not start at zero, because the encoding is position and slope, not length; but then the chart must not claim a large change that is small in relative terms, and the axis range must be stated by the labels.

### 6.2 The dual-axis chart

Two series with two y-axes can be made to say anything, because each axis has its own scale and you choose both.

```python run
airport = sales[sales["store"] == "Airport"].groupby(sales["date"].dt.to_period("M").dt.to_timestamp())["revenue"].sum() / 1000
harbour = sales[sales["store"] == "Harbour"].groupby(sales["date"].dt.to_period("M").dt.to_timestamp())["revenue"].sum() / 1000
print("correlation of the two monthly series:", round(float(airport.corr(harbour)), 2))


def dual_axis(ylim_left, ylim_right):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax2 = ax.twinx()
    ax.plot(airport.index, airport.values, color="#D55E00")
    ax2.plot(harbour.index, harbour.values, color="#0072B2")
    ax.set_ylim(*ylim_left)
    ax2.set_ylim(*ylim_right)
    fig.canvas.draw()
    return fig, ax, ax2


def first_crossing(ax, ax2):
    """Months in which the left line is drawn ABOVE the right line, as the eye sees it (in axes fractions)."""
    l = (ax.lines[0].get_ydata() - ax.get_ylim()[0]) / np.diff(ax.get_ylim())[0]
    r = (ax2.lines[0].get_ydata() - ax2.get_ylim()[0]) / np.diff(ax2.get_ylim())[0]
    return int((l > r).sum()), len(l)


print("monthly revenue range (thousands): Airport", round(airport.min()), "to", round(airport.max()), "| Harbour", round(harbour.min()), "to", round(harbour.max()))
for label, a, b in [("same scale on both axes", (0, 60), (0, 60)), ("right axis 0 to 45", (0, 60), (0, 45)), ("right axis 10 to 55", (0, 60), (10, 55))]:
    fig, ax, ax2 = dual_axis(a, b)
    above, n = first_crossing(ax, ax2)
    print(f"{label:24} the Airport line is drawn above the Harbour line in {above} of {n} months")
    plt.close(fig)
```
```text
correlation of the two monthly series: 0.98
monthly revenue range (thousands): Airport 34 to 46 | Harbour 31 to 43
same scale on both axes  the Airport line is drawn above the Harbour line in 24 of 24 months
right axis 0 to 45       the Airport line is drawn above the Harbour line in 0 of 24 months
right axis 10 to 55      the Airport line is drawn above the Harbour line in 24 of 24 months
```

The data never changed, and neither did the correlation (0.98), yet by changing only the limits of one axis we can make the orange line sit above the blue one in every month, or in none. In truth Airport is higher than Harbour in every month, by 3 to 4 thousand; with the second scale the picture says the opposite. A reader sees *crossings* and *gaps* that are artefacts of two arbitrary scales. Alternatives: plot both series on **one axis** if they share a unit (here they do), use **indexed** series (each divided by its own first value, so both start at 100), or use two stacked small panels with a shared x-axis.

```python run
idx = pd.DataFrame({"Airport": airport / airport.iloc[0] * 100, "Harbour": harbour / harbour.iloc[0] * 100})
print(idx.round(0).iloc[[0, 11, 23]].to_string())
```
```text
            Airport  Harbour
date                        
2023-01-01   100.00   100.00
2023-12-01   110.00   114.00
2024-12-01   124.00   124.00
```

### 6.3 Size and area

When a number is encoded as the size of a circle, there are two ways to scale it, and one is a lie. `scatter(s=...)` sets the **area** (in points squared). If you set `s` proportional to the value, the *area* is proportional to the value and the picture is honest. If you set the **radius** proportional to the value, doubling the value quadruples the area, and the eye reads the area.

```python run
vals = np.array([1.0, 2.0, 4.0])
area_honest = vals * 100                           # area proportional to the value
area_lying = (vals * 10) ** 2                      # radius proportional to the value -> area grows with the square
print("data ratios            :", (vals / vals[0]).tolist())
print("area, s proportional   :", (area_honest / area_honest[0]).tolist())
print("area, radius prop.     :", (area_lying / area_lying[0]).tolist(), "<- the 4x value looks 16x bigger")
```
```text
data ratios            : [1.0, 2.0, 4.0]
area, s proportional   : [1.0, 2.0, 4.0]
area, radius prop.     : [1.0, 4.0, 16.0] <- the 4x value looks 16x bigger
```

Even the honest version is a weak encoding (people under-estimate areas), so use size only as a *secondary* channel (a bubble for the third variable), never for the main comparison.

### 6.4 Pies, 3D and decoration

A pie chart encodes numbers as **angles and areas**; a 3D pie or a 3D bar adds perspective that makes the front slice look larger than the back. These are the weakest encodings in section 1. The rule of thumb: if you need the reader to rank or compare, use bars. A pie is defensible only for two or three slices where the point is "about half" or "a small part", and always with the values printed.

Chart *decoration* (gradients, shadows, background images, icons for bars) does not carry data and competes with it. Tufte called the ink that carries no data **chartjunk**; the test for any element is: if I remove it, does the reader lose information? If not, remove it.

### 6.5 Cherry-picked windows

A line chart of a short window can show any story. Find the worst 3-month window in our monthly series, and draw it next to the whole history.

```python run
roll = monthly.rolling(3).apply(lambda s: s.iloc[-1] / s.iloc[0] - 1, raw=False)
worst_end = roll.idxmin()
window = monthly.loc[:worst_end].iloc[-3:]
print("worst 3-month window:", window.index[0].date(), "to", window.index[-1].date(),
      "| change within the window:", f"{(window.iloc[-1] / window.iloc[0] - 1) * 100:.1f}%")
print("whole period, first to last month:", f"{(monthly.iloc[-1] / monthly.iloc[0] - 1) * 100:+.1f}%")
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), layout="constrained")
axes[0].plot(window.index, window.values / 1000, marker="o", color="#D55E00")
axes[0].set_title("Revenue is falling!", loc="left")
axes[1].plot(monthly.index, monthly.values / 1000, marker="o", color="#1b6ca8")
axes[1].axvspan(window.index[0], window.index[-1], color="#D55E00", alpha=.2)
axes[1].set_title("...inside two years of growth", loc="left")
for ax in axes:
    ax.set_ylabel("Monthly revenue (thousands)")
describe_fig(fig)
plt.close(fig)
```
```text
worst 3-month window: 2023-12-01 to 2024-02-01 | change within the window: -5.3%
whole period, first to last month: +23.5%
figure 10 x 3.4 inches, 2 axes
  axes[0] title='Revenue is falling!'  xlabel=''  ylabel='Monthly revenue (thousands)'
           xlim=(19689, 19757)  ylim=(178.19, 189.25)  lines=1 patches=0 collections=0 texts=0
  axes[1] title='...inside two years of growth'  xlabel=''  ylabel='Monthly revenue (thousands)'
           xlim=(19323, 20093)  ylim=(151.97, 211.49)  lines=1 patches=1 collections=0 texts=0
```

Every statement of the left panel is true and its message is false. The defences: show the **full range** (or at least a comparable earlier period), state the window and **why** you chose it, and be suspicious of any chart whose start date looks arbitrary. This is the same disease as p-hacking in da.08: choosing the view after seeing the data.

### 6.6 Aspect ratio and slope

The eye judges a trend by the **angle** of the line, and the angle depends on the shape of the plot area, not only on the data. A wide, flat figure makes growth look gentle; a tall, narrow one makes the same growth look steep.

```python run
def line_angle(ax):
    """The angle (in degrees) of the straight line from the first to the last point, as drawn in the plot area."""
    fig = ax.figure
    fig.canvas.draw()
    x, y = ax.lines[0].get_xdata(), ax.lines[0].get_ydata()
    x = mdates.date2num(x) if np.issubdtype(np.asarray(x).dtype, np.datetime64) else np.asarray(x, float)
    bb = ax.get_window_extent()
    xl, yl = ax.get_xlim(), ax.get_ylim()
    dx = (x[-1] - x[0]) / (xl[1] - xl[0]) * bb.width
    dy = (y[-1] - y[0]) / (yl[1] - yl[0]) * bb.height
    return float(np.degrees(np.arctan2(dy, dx)))


for size in [(10, 2.5), (6, 5), (3, 6)]:
    fig, ax = plt.subplots(figsize=size)
    ax.plot(monthly.index, monthly.values / 1000)
    ax.set_ylim(0, None)
    print(f"figure {size[0]:>4} x {size[1]:<4} inches: the same data rise at {line_angle(ax):4.1f} degrees")
    plt.close(fig)
```
```text
figure   10 x 2.5  inches: the same data rise at  2.9 degrees
figure    6 x 5    inches: the same data rise at  9.7 degrees
figure    3 x 6    inches: the same data rise at 22.3 degrees
```

The same two years of revenue rise at an angle that changes with the figure's shape. The guideline known as **banking to 45 degrees** says to choose the aspect ratio so that the important slopes sit near 45 degrees, where the eye judges changes best. In practice: do not squeeze a time series into a thin strip to make it look calm, and do not stretch it to make it look dramatic. Keep one consistent shape for charts that will be compared.

### 6.7 Missing data drawn as data

A line connects consecutive points. If a gap in the data is hidden (by interpolating, or by plotting an index of dates where the missing ones were dropped), the line implies values that were never observed. Riverside's closure is the example: if the weekly series is interpolated, the chart claims sales during the weeks the store was shut.

```python run
riv = weekly_store["Riverside"]
interp = riv.interpolate()
phantom = (interp[riv.isna()]).sum()
print(f"weeks with no data: {int(riv.isna().sum())}")
print(f"revenue the interpolated line implies for those weeks: {phantom:,.1f} thousand (observed: 0)")
print(f"that is {phantom / riv.sum() * 100:.1f}% of Riverside's total in the chart")
```
```text
weeks with no data: 4
revenue the interpolated line implies for those weeks: 19.8 thousand (observed: 0)
that is 4.0% of Riverside's total in the chart
```

Break the line (as in 4.2), or draw the closure as a shaded band with a label. And if a **time axis is categorical** (months as text labels, with missing months simply absent), the spacing lies: neighbouring points look one step apart whether they are one month or six apart. Use real dates on the x-axis so that the gaps are proportional.

### 6.8 Inconsistent scales between panels

Panels that are meant to be compared must share axes. With free y-axes, a tiny category looks as large as a big one.

```python run
panels = {"espresso": cat_month["espresso"], "pastry": cat_month["pastry"]}
fig, axes = plt.subplots(1, 2, figsize=(8, 3), sharey=False, layout="constrained")
for ax, (name, s) in zip(axes, panels.items()):
    ax.plot(s.index, s.values)
    ax.set_title(name, loc="left")
fig.canvas.draw()
heights = [(a.lines[0].get_ydata().max() - a.get_ylim()[0]) / np.diff(a.get_ylim())[0] for a in axes]
print("how high the peak reaches in each panel (share of panel height):", [round(float(h), 2) for h in heights])
print("actual peaks (thousands):", {k: round(float(s.max()), 1) for k, s in panels.items()})
print("ratio of the real peaks:", round(float(cat_month['espresso'].max() / cat_month['pastry'].max()), 2))
plt.close(fig)
```
```text
how high the peak reaches in each panel (share of panel height): [0.95, 0.95]
actual peaks (thousands): {'espresso': 81.7, 'pastry': 66.0}
ratio of the real peaks: 1.24
```

Both peaks reach the top of their own panel, so the eye says "the same size", although espresso's peak is about a quarter higher than pastry's (81.7 against 66.0, a ratio of 1.24), and in total espresso sells almost twice what pastry does. Use `sharey=True` for comparisons, or put both series in one panel.

### 6.9 Colour maps that deceive

The `jet` / rainbow colour map is the classic offender: its lightness goes up, down and up again, so it creates false boundaries where the data are smooth, and it cannot be read in greyscale. A good sequential map has lightness that changes in **one direction**. We can test it numerically by converting each colour to luminance.

```python run
def luminance_profile(name, n=64):
    rgb = matplotlib.colormaps[name](np.linspace(0, 1, n))[:, :3]
    return rgb @ np.array([0.2126, 0.7152, 0.0722])


for name in ("viridis", "cividis", "Blues", "jet", "rainbow"):
    lum = luminance_profile(name)
    d = np.diff(lum)
    direction_changes = int(np.sum(np.sign(d[1:]) != np.sign(d[:-1])))
    print(f"{name:8} luminance at the start {lum[0]:.2f}, peak {lum.max():.2f} at {lum.argmax() / (len(lum) - 1):.0%} of the way, end {lum[-1]:.2f}; direction changes: {direction_changes}")
```
```text
viridis  luminance at the start 0.08, peak 0.87 at 100% of the way, end 0.87; direction changes: 0
cividis  luminance at the start 0.12, peak 0.88 at 100% of the way, end 0.88; direction changes: 0
Blues    luminance at the start 0.98, peak 0.98 at 0% of the way, end 0.17; direction changes: 0
jet      luminance at the start 0.04, peak 0.91 at 63% of the way, end 0.11; direction changes: 1
rainbow  luminance at the start 0.18, peak 0.88 at 54% of the way, end 0.21; direction changes: 1
```

A perceptually sensible map gets steadily lighter or steadily darker (zero direction changes). `jet` and `rainbow` rise to a bright peak in the middle (the cyan-yellow band, 54 to 63 percent of the way) and fall again, so two values far apart on the scale can have the same lightness, and the bright band looks like a boundary in the data. Use `viridis`, `cividis`, or single-hue maps like `Blues` for sequential data, and a proper diverging map (`RdBu`, `vlag`) with the centre at a meaningful value.

### 6.10 An honesty checklist

| Check | A chart fails if... |
|---|---|
| Baseline | a bar chart does not start at 0 |
| Lie factor | the visual change is far from the data change |
| Scale | panels that are compared have different axes; two axes are used to suggest a link |
| Window | the time range hides context, or looks cherry-picked |
| Gaps | missing data are interpolated or hidden |
| Encoding | the main comparison uses area, angle, 3D or colour |
| Colour | the map is not perceptually ordered or not colour-blind safe |
| Labels | no units, no source, no `n`, no definition of the interval |
| Title | the title claims more than the chart shows (causes, "proves") |

## 7. Interactive charts with plotly

### 7.1 When interactivity helps

An interactive chart lets the reader hover for exact values, zoom into a period, hide a series by clicking its legend entry, and play an animation. That is valuable for **exploration** and for **dashboards**: the reader can answer his own follow-up questions. It is wasted in print, in a slide that will be shown for 20 seconds, or when the key message needs the reader to click to discover it. The rule: **the default view must tell the story**; interaction is for the details.

**plotly** draws charts as JSON that a JavaScript library renders in the browser. Two interfaces: **plotly express** (`px`), one call per chart from a tidy DataFrame, like seaborn; and **graph objects** (`go`), explicit control of every trace and layout option.

### 7.2 A chart in one call

```python run
def describe_plotly(fig):
    """Print what a plotly figure contains (the counterpart of describe_fig)."""
    lay = fig.layout
    title = lay.title.text if lay.title and lay.title.text else None
    print(f"figure title={title!r} | traces={len(fig.data)} | xaxis={lay.xaxis.title.text!r} | yaxis={lay.yaxis.title.text!r}")
    for i, tr in enumerate(fig.data[:6]):
        n = len(tr.x) if tr.x is not None else 0
        print(f"  trace[{i}] type={tr.type!r} name={tr.name!r} points={n}")
    if len(fig.data) > 6:
        print(f"  ... and {len(fig.data) - 6} more traces")


mw = (sales.assign(month=sales["date"].dt.to_period("M").dt.to_timestamp())
           .groupby(["month", "store"], as_index=False)["revenue"].sum())
fig = px.line(mw, x="month", y="revenue", color="store", markers=True, title="Monthly revenue by store",
              labels={"revenue": "Monthly revenue", "month": "", "store": "Store"},
              color_discrete_map=STORE_COLOR)
describe_plotly(fig)
print("colour of the first trace:", fig.data[0].line.color, "| store:", fig.data[0].name)
```
```text
figure title='Monthly revenue by store' | traces=6 | xaxis='' | yaxis='Monthly revenue'
  trace[0] type='scatter' name='Airport' points=24
  trace[1] type='scatter' name='Campus' points=24
  trace[2] type='scatter' name='Harbour' points=24
  trace[3] type='scatter' name='Mall' points=24
  trace[4] type='scatter' name='Old Town' points=24
  trace[5] type='scatter' name='Riverside' points=24
colour of the first trace: #F0E442 | store: Airport
```

One call created six traces (one per store) with a legend, hover text and zoom. `color_discrete_map` applies our consistent store colours (section 3.6). The result is a `Figure` object whose structure you can inspect and edit.

### 7.3 Hover text, layout and facets

The default hover shows the raw column names; a good one reads like a sentence. `hovertemplate` writes it.

```python run
fig.update_traces(hovertemplate="%{fullData.name}<br>%{x|%b %Y}: %{y:,.0f}<extra></extra>")
fig.update_layout(template="plotly_white", hovermode="x unified", legend_title_text="", yaxis_tickformat=",.0f",
                  margin={"l": 60, "r": 20, "t": 60, "b": 40})
print("hover template:", fig.data[0].hovertemplate)
print("hover mode    :", fig.layout.hovermode, "| template:", fig.layout.template.layout.paper_bgcolor)
```
```text
hover template: %{fullData.name}<br>%{x|%b %Y}: %{y:,.0f}<extra></extra>
hover mode    : x unified | template: white
```

`hovermode="x unified"` shows all stores for the hovered month in one box, which is the natural reading for a multi-line chart. `<extra></extra>` removes the trace-name side box. Facets work as in seaborn:

```python run
fig_f = px.bar(sales.groupby(["store", "category"], as_index=False)["revenue"].sum(), x="category", y="revenue",
               facet_col="store", facet_col_wrap=3, color="category", title="Revenue by category, one panel per store",
               color_discrete_map=CAT_COLOR, height=450)
fig_f.update_yaxes(matches="y")                                    # one shared y-scale, as in section 3.5
fig_f.update_layout(showlegend=False)
describe_plotly(fig_f)
print("panels:", len([k for k in fig_f.layout if k.startswith("xaxis")]), "| shared y:", all(fig_f.layout[k].matches == "y" for k in fig_f.layout if k.startswith("yaxis") and k != "yaxis"))
```
```text
figure title='Revenue by category, one panel per store' | traces=24 | xaxis='category' | yaxis='revenue'
  trace[0] type='bar' name='cold' points=1
  trace[1] type='bar' name='cold' points=1
  trace[2] type='bar' name='cold' points=1
  trace[3] type='bar' name='cold' points=1
  trace[4] type='bar' name='cold' points=1
  trace[5] type='bar' name='cold' points=1
  ... and 18 more traces
panels: 6 | shared y: True
```

### 7.4 Animation

An **animation** adds a time slider and a play button: one frame per value of `animation_frame`. Use it sparingly: the eye cannot compare frames well, so animations suit "what happens" stories, not precise comparisons. Fix the axis ranges so that the frames are comparable.

```python run
qq = (sales.assign(quarter=sales["date"].dt.to_period("Q").astype(str))
           .groupby(["quarter", "store"], as_index=False)["revenue"].sum())
fig_a = px.bar(qq, x="store", y="revenue", color="store", animation_frame="quarter", color_discrete_map=STORE_COLOR,
               range_y=[0, qq["revenue"].max() * 1.1], title="Revenue by store, quarter by quarter")
print("frames:", len(fig_a.frames), "| first/last:", fig_a.frames[0].name, fig_a.frames[-1].name)
print("y-axis fixed across frames:", [round(v) for v in fig_a.layout.yaxis.range])
```
```text
frames: 8 | first/last: 2023Q1 2024Q4
y-axis fixed across frames: [0, 149519]
```

### 7.5 Graph objects and subplots

When you need exact control, build the traces yourself. This also shows what `px` does for you.

```python run
from plotly.subplots import make_subplots

tot = sales.groupby("date")["revenue"].sum()
fig_g = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05,
                      subplot_titles=("Daily revenue", "Average temperature"))
fig_g.add_trace(go.Scatter(x=tot.index, y=tot.values, mode="lines", name="revenue", line={"color": "#1b6ca8"}), row=1, col=1)
temps = sales.groupby("date")["temp_c"].first()
fig_g.add_trace(go.Scatter(x=temps.index, y=temps.values, mode="lines", name="temperature (C)", line={"color": "#D55E00"}), row=2, col=1)
fig_g.update_layout(template="plotly_white", showlegend=False, height=500, title="Revenue and temperature share one time axis")
print("traces:", len(fig_g.data), "| rows of subplots:", len([k for k in fig_g.layout if k.startswith("yaxis")]))
print("points in the first trace:", len(fig_g.data[0].x))
```
```text
traces: 2 | rows of subplots: 2
points in the first trace: 731
```

This is the better alternative to the dual-axis chart of 6.2: two panels, one shared time axis, each with its own honest y-axis.

### 7.6 Saving and sharing

A plotly figure is saved as a self-contained **HTML** file that opens in any browser. `include_plotlyjs=True` embeds the whole library (about 4 to 5 MB), which makes the file work offline; `"cdn"` links to a copy on the internet (a small file, but it needs a connection); `"directory"` writes one shared `plotly.min.js` next to the files.

```python run
fig.write_html(tmp / "monthly_by_store.html", include_plotlyjs=True)
fig.write_html(tmp / "monthly_by_store_cdn.html", include_plotlyjs="cdn")
for f in ("monthly_by_store.html", "monthly_by_store_cdn.html"):
    print(f"{f:28} {(tmp / f).stat().st_size / 1024:9.0f} KB (machine-specific)")
text = (tmp / "monthly_by_store.html").read_text()
print("HTML contains the data:", "Airport" in text, "| and the library:", "plotly" in text.lower())
print("JSON of the figure starts with:", fig.to_json()[:60], "...")
```
```text
monthly_by_store.html             4718 KB (machine-specific)
monthly_by_store_cdn.html           15 KB (machine-specific)
HTML contains the data: True | and the library: True
JSON of the figure starts with: {"data":[{"hovertemplate":"%{fullData.name}\u003cbr\u003e%{x ...
```

For a **static** image (PDF or PNG for a report), plotly needs an extra package (kaleido); matplotlib is simpler for print. A common workflow: matplotlib or seaborn for reports, plotly for dashboards and exploration.

### 7.7 Interactive design rules

1. The **initial view** answers the main question without any click.
2. **Hover** adds precision, not the only way to see the data (no one can hover on a printed copy or a phone).
3. Keep **colour consistent** with your static charts.
4. Set the **axis ranges** deliberately (animations, zoomed views).
5. Make the title and units readable without interaction.
6. Test with the default window size: many dashboards look fine on a developer's large screen and break on a laptop.

## 8. Design for the reader

### 8.1 The title is the message

A topic title ("Revenue by store") makes the reader work out what to conclude. A **finding title** ("Airport sells 1.9 times as much as Riverside") gives the conclusion and lets the chart prove it. Write the finding, put the topic and units in a subtitle or axis label, and check the finding with code, as in 3.2. Never state a cause the chart cannot support; "goes with" and "is associated with" are the honest verbs of da.08.

```python run
ratio = rev_store["Airport"] / rev_store["Riverside"]
print(f"Airport / Riverside revenue ratio: {ratio:.2f}")
title = f"Airport sells {ratio:.1f} times as much as Riverside"
print("title:", title)
```
```text
Airport / Riverside revenue ratio: 1.93
title: Airport sells 1.9 times as much as Riverside
```

### 8.2 Contrast and colour-blind safety

Text and marks need enough contrast against the background (the WCAG guideline asks for a contrast ratio of at least 4.5 for normal text and 3 for large text and graphics). The ratio is computed from the relative luminance of the two colours.

```python run
def rel_luminance(hex_color):
    rgb = np.array(matplotlib.colors.to_rgb(hex_color))
    lin = np.where(rgb <= .03928, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    return float(lin @ np.array([0.2126, 0.7152, 0.0722]))


def contrast_ratio(fg, bg="#ffffff"):
    a, b = rel_luminance(fg), rel_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + .05) / (lo + .05)


for name, c in [("black", "#000000"), ("dark gray", "#555555"), ("light gray", "#bbbbbb"), ("Okabe yellow", "#F0E442"), ("Okabe blue", "#0072B2")]:
    r = contrast_ratio(c)
    print(f"{name:13} {c}  contrast on white {r:5.2f}  {'passes 3:1 (graphics)' if r >= 3 else 'FAILS 3:1'}")
```
```text
black         #000000  contrast on white 21.00  passes 3:1 (graphics)
dark gray     #555555  contrast on white  7.46  passes 3:1 (graphics)
light gray    #bbbbbb  contrast on white  1.92  FAILS 3:1
Okabe yellow  #F0E442  contrast on white  1.32  FAILS 3:1
Okabe blue    #0072B2  contrast on white  5.19  passes 3:1 (graphics)
```

Light gray and yellow lines on white are barely visible; the Okabe yellow `#F0E442` is only for **filled areas or points with an outline**, never for thin lines on white. We assigned yellow to Airport in `STORE_COLOR`, which is fine for fat bars and a poor choice for a thin line: a design decision to revisit when drawing lines.

Colour-blindness is a different problem: some colour pairs look the same. We can simulate the most common kind (red-green, "deuteranopia") with a matrix and measure how much two colours stay apart afterwards.

```python run
DEUTAN = np.array([[0.625, 0.375, 0.0], [0.700, 0.300, 0.0], [0.0, 0.300, 0.700]])      # an approximate simulation of red-green blindness


def simulate(hex_color):
    return np.clip(DEUTAN @ np.array(matplotlib.colors.to_rgb(hex_color)), 0, 1)


def separation(c1, c2, simulated=True):
    a = simulate(c1) if simulated else np.array(matplotlib.colors.to_rgb(c1))
    b = simulate(c2) if simulated else np.array(matplotlib.colors.to_rgb(c2))
    return float(np.linalg.norm(a - b))


pairs = [("red and green", "#d62728", "#2ca02c"), ("orange and blue (Okabe)", "#E69F00", "#0072B2"), ("vermillion and bluish green", "#D55E00", "#009E73")]
for name, c1, c2 in pairs:
    print(f"{name:28} distance normal vision {separation(c1, c2, False):.2f} | with red-green blindness {separation(c1, c2):.2f}")
```
```text
red and green                distance normal vision 0.82 | with red-green blindness 0.43
orange and blue (Okabe)      distance normal vision 1.15 | with red-green blindness 1.03
vermillion and bluish green  distance normal vision 0.98 | with red-green blindness 0.77
```

The classic red/green pair loses about half of its separation under the simulation (0.82 to 0.43), while orange/blue hardly changes (1.15 to 1.03). Pairs that differ in *lightness* as well as hue survive best. Two additional defences: **do not rely on colour alone** (add direct labels, markers or line styles), and use the colour-blind-safe palettes of section 3.6.

### 8.3 Direct labels, order and ink

- **Label directly** when you can (the name at the end of a line, the value on a bar), and drop the legend that forces the eye to travel.
- **Order the categories** by value (or by a natural order such as months), not alphabetically, unless the reader will look up a name.
- **Remove ink that carries no data**: frame lines, heavy grids, repeated labels, 3D effects, background colours.
- **Use one scale and one colour per entity** across all charts of a report.

```python run
fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
for store in weekly_store.columns:
    s = weekly_store[store].rolling(4, min_periods=1).mean()
    ax.plot(s.index, s.values, color=STORE_COLOR[store] if store != "Airport" else "#B8A800", linewidth=1.6)
    ax.text(s.index[-1] + pd.Timedelta(days=5), s.dropna().iloc[-1], store, va="center", fontsize=9)
ax.set_xlim(right=weekly_store.index[-1] + pd.Timedelta(days=60))
ax.set_ylabel("Weekly revenue, 4-week average (thousands)")
ax.set_title("Stores keep their ranking all year", loc="left")
ax.spines[["top", "right"]].set_visible(False)
describe_fig(fig)
print("labels written on the chart:", [t.get_text() for t in ax.texts])
print("legend present:", ax.get_legend() is not None)
plt.close(fig)
```
```text
figure 8 x 4 inches, 1 axes
  axes[0] title='Stores keep their ranking all year'  xlabel=''  ylabel='Weekly revenue, 4-week average (thousands)'
           xlim=(19329, 20146)  ylim=(3.9961, 10.767)  lines=6 patches=0 collections=0 texts=6
labels written on the chart: ['Airport', 'Campus', 'Harbour', 'Mall', 'Old Town', 'Riverside']
legend present: False
```

The names sit at the line ends; the legend is gone. (We also darkened the yellow for Airport so the line is visible.) The title is a claim; we should confirm it:

```python run
rank_by_year = sales.groupby([sales["date"].dt.year, "store"])["revenue"].sum().groupby(level=0).rank(ascending=False).unstack(0).astype(int)
print(rank_by_year.to_string())
print("ranking unchanged between 2023 and 2024:", bool((rank_by_year[2023] == rank_by_year[2024]).all()))
```
```text
date       2023  2024
store                
Airport       1     1
Campus        5     5
Harbour       2     2
Mall          3     3
Old Town      4     4
Riverside     6     6
ranking unchanged between 2023 and 2024: True
```

### 8.4 Design for the destination

The same chart is designed differently for different readers.

| Destination | Size and text | Detail | Format |
|---|---|---|---|
| Slide, shown for seconds | large fonts (talk context, 16+ pt), 16:9 | one message, few marks | PNG 150-200 dpi |
| Printed report | text 8-10 pt, column width 3.3 or 6.8 in | more detail, captions | PDF or SVG |
| Dashboard | readable at a glance, consistent filters | interactive detail on hover | plotly HTML |
| Email or chat | self-explanatory: full title, source, units | simple | PNG |

```python run
for dest, size, ctx in [("slide", (10, 5.6), "talk"), ("report column", (3.3, 2.4), "paper"), ("dashboard tile", (5, 3), "notebook")]:
    with sns.plotting_context(ctx):
        fig, ax = plt.subplots(figsize=size)
        ax.plot([0, 1], [0, 1])
        ax.set_title("Title")
        fig.canvas.draw()
        print(f"{dest:15} {size[0]:>4} x {size[1]:<4} in | font size {plt.rcParams['font.size']:4.1f} | title size {ax.title.get_fontsize():4.1f} pt")
        plt.close(fig)
```
```text
slide             10 x 5.6  in | font size 18.0 | title size 18.0 pt
report column    3.3 x 2.4  in | font size  9.6 | title size  9.6 pt
dashboard tile     5 x 3    in | font size 12.0 | title size 12.0 pt
```

### 8.5 Alt text and captions

A chart without a text equivalent is invisible to screen readers and useless in a text-only message. Write a short description for every chart: **type, what is on each axis, the main pattern, and the takeaway**. Our `describe_fig` gives the raw facts; add the interpretation.

```python run
ALT = ("Line chart of BrewCo monthly revenue from January 2023 to December 2024, in thousands. "
       f"Revenue rises from about {monthly.iloc[0] / 1000:,.0f} to {monthly.iloc[-1] / 1000:,.0f}, "
       f"a growth of {(yearly[2024] / yearly[2023] - 1) * 100:.0f}% from 2023 to 2024, with no strong seasonal peak.")
print(ALT)
```
```text
Line chart of BrewCo monthly revenue from January 2023 to December 2024, in thousands. Revenue rises from about 169 to 209, a growth of 11% from 2023 to 2024, with no strong seasonal peak.
```

> **Try it.** Write an alt text for the diverging satisfaction chart of 4.6 using the data: say which store is the least satisfied and by how much, built from `net` rather than typed.

<details><summary>Answer</summary>

```python run
worst, best = net.index[0], net.index[-1]
alt = (f"Horizontal bar chart of net satisfaction (percent rating 4-5 minus percent rating 1-2) for six stores. "
       f"{worst} is the only store below zero at {net.iloc[0]:+.0f}; {best} is highest at {net.iloc[-1]:+.0f}. "
       f"Each store has 300 survey answers.")
print(alt)
```
```text
Horizontal bar chart of net satisfaction (percent rating 4-5 minus percent rating 1-2) for six stores. Airport is the only store below zero at -2; Campus is highest at +74. Each store has 300 survey answers.
```

Because the numbers come from the data, the alt text updates when the data do. A hand-typed caption is the first thing to go stale.

</details>


## 9. Testing your charts

### 9.1 Why test a picture?

A chart is code, and code can be wrong in ways that look fine: a bar axis that starts at 2.0, a legend with the series swapped, a title that says "growth" over falling numbers, a figure whose tiny font is unreadable on a slide. Nobody notices until a decision rests on it. The cheap defence is to **test the structure of the figure**: not its pixels, but what it contains. matplotlib makes this possible because a figure is an object tree that you can inspect (section 3.1), and plotly's figure is a tree of properties too.

Two rules make charts testable.

1. **Put each chart in a function that returns the `Figure`** (and does not call `plt.show()` or save it). The function takes the data as an argument, so a test can give it a tiny table with a known answer.
2. **Separate preparing the data from drawing it.** A small function builds the numbers (testable with ordinary asserts), and another draws them.

### 9.2 Reading data back from a figure

Every artist keeps the data it was given. Small helpers extract them:

```python run
def bar_values(ax):
    """(label, value) for each bar of a vertical or horizontal bar chart."""
    ax.figure.canvas.draw()
    patches = [p for p in ax.patches]
    horizontal = len({round(p.get_height(), 6) for p in patches}) == 1 and len({round(p.get_width(), 6) for p in patches}) > 1
    if horizontal:
        labels = [t.get_text() for t in ax.get_yticklabels()]
        return list(zip(labels, [float(p.get_width()) for p in patches]))
    labels = [t.get_text() for t in ax.get_xticklabels()]
    return list(zip(labels, [float(p.get_height()) for p in patches]))


def line_data(ax, i=0):
    ln = ax.lines[i]
    return np.asarray(ln.get_xdata()), np.asarray(ln.get_ydata(), float)


def make_store_bars(sales_df):
    """Data step: revenue per store, sorted. Drawing step: a horizontal bar chart. Returns the Figure."""
    s = sales_df.groupby("store")["revenue"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(6, 3), layout="constrained")
    ax.barh(s.index, s.values / 1000, color="#1b6ca8")
    ax.set_xlabel("Revenue (thousands)")
    ax.set_title("Revenue by store")
    return fig


tiny = pd.DataFrame({"store": ["A", "A", "B", "C"], "revenue": [100.0, 50.0, 400.0, 220.0], "date": pd.Timestamp("2025-01-01")})
fig = make_store_bars(tiny)
print(bar_values(fig.axes[0]))
plt.close(fig)
```
```text
[('A', 0.15), ('C', 0.22), ('B', 0.4)]
```

With a tiny table whose answer we know by hand (A = 150, B = 400, C = 220 in thousands: 0.15, 0.4, 0.22), the chart's data can be checked exactly, and the sorted order of the bars verified: smallest at the bottom.

```python run
def test_store_bars():
    fig = make_store_bars(tiny)
    got = dict(bar_values(fig.axes[0]))
    expected = {"A": 0.15, "C": 0.22, "B": 0.4}
    assert set(got) == set(expected) and all(abs(got[k] - v) < 1e-9 for k, v in expected.items()), f"bar values are wrong: {got}"
    order = [k for k, _ in bar_values(fig.axes[0])]
    assert order == ["A", "C", "B"], f"bars should be sorted from smallest to largest, got {order}"
    assert fig.axes[0].get_xlim()[0] <= 0, "the value axis of a bar chart must start at 0"
    plt.close(fig)


test_store_bars()
print("test_store_bars passed")
```
```text
test_store_bars passed
```

Every assertion has a message that names the likely mistake: the same rule as in all the tests of this module.

### 9.3 A chart linter

Some rules apply to every chart. A **linter** checks them automatically and lists the problems, the way a code linter does. Ours covers the checks of the honesty list (6.10) that a program can decide.

```python run
def lint_figure(fig, min_font=8.0, max_legend=7):
    """Return a list of problems found in a matplotlib figure."""
    fig.canvas.draw()
    issues = []
    for i, ax in enumerate(fig.axes):
        if ax.get_label() == "<colorbar>":
            continue
        name = f"axes[{i}]"
        title = ax.get_title() or ax.get_title(loc="left") or ax.get_title(loc="right")
        if not title and not (fig._suptitle and fig._suptitle.get_text()):
            issues.append(f"{name}: no title")
        has_data = bool(ax.lines or ax.patches or ax.collections)
        if has_data and not ax.images:
            family = ax.get_shared_x_axes().get_siblings(ax) + ax.get_shared_y_axes().get_siblings(ax)       # panels that share an axis
            if not any(a.get_xlabel() or a.get_ylabel() for a in family) and not ax.get_xlabel() and not ax.get_ylabel():
                issues.append(f"{name}: no axis labels (units?)")
        patches = [p for p in ax.patches if p.get_width() > 0 and p.get_height() > 0 or p.get_height() != 0 or p.get_width() != 0]
        if patches and not ax.lines:
            heights, widths = {round(p.get_height(), 6) for p in patches}, {round(p.get_width(), 6) for p in patches}
            if len(widths) == 1 and len(heights) > 1 or (len(widths) == 1 and len(patches) > 1):       # vertical bars
                if ax.get_ylim()[0] > 0:
                    issues.append(f"{name}: bar chart value axis starts at {ax.get_ylim()[0]:g}, not 0 (the lie factor is not 1)")
            elif len(heights) == 1:                                                                      # horizontal bars
                if ax.get_xlim()[0] > 0:
                    issues.append(f"{name}: bar chart value axis starts at {ax.get_xlim()[0]:g}, not 0 (the lie factor is not 1)")
        leg = ax.get_legend()
        if leg and len(leg.get_texts()) > max_legend:
            issues.append(f"{name}: legend has {len(leg.get_texts())} entries (more than {max_legend}): use small multiples")
        series = [ln for ln in ax.lines if len(ln.get_xdata()) > 2]                                            # error-bar caps are not series
        if len(series) > 1 and not leg and not ax.texts:
            issues.append(f"{name}: {len(series)} lines but no legend and no direct labels")
    small = {round(t.get_fontsize(), 1) for t in fig.findobj(matplotlib.text.Text) if t.get_visible() and t.get_text().strip() and t.get_fontsize() < min_font}
    if small:
        issues.append(f"text smaller than {min_font:g} pt: sizes {sorted(small)}")
    return issues


# a good chart
good = make_store_bars(tiny)
print("good chart:", lint_figure(good) or "no problems")
plt.close(good)

# a bad chart: truncated axis, no title, no labels, tiny text
bad, ax = plt.subplots()
ax.bar(["2023", "2024"], [2.108, 2.344])
ax.set_ylim(2.0, 2.4)
ax.text(0, 2.35, "growth!", fontsize=5)
for issue in lint_figure(bad):
    print("  -", issue)
plt.close(bad)
```
```text
good chart: no problems
  - axes[0]: no title
  - axes[0]: no axis labels (units?)
  - axes[0]: bar chart value axis starts at 2, not 0 (the lie factor is not 1)
  - text smaller than 8 pt: sizes [5.0]
```

The linter finds four problems in the bad chart that a quick look might miss: it has no title, no labels, a truncated axis and unreadable text. (A first version of this linter flagged our own report below: panels that share an axis carry one label for all, and the caps of an error bar are lines but not series. We taught the linter about both. A linter has to be tuned on real charts, like a spell checker.) It cannot judge everything (whether the chart answers the question, whether the colours are chosen well, whether the story is true), but it catches the mechanical failures, and it never gets tired. Run it on every figure before it leaves your machine.

### 9.4 Testing a title against the data

A title that states a number is an assertion. Make the title come from the data (as in 3.2), and test the relationship between the two.

```python run
def make_growth_chart(sales_df):
    m = sales_df.groupby(sales_df["date"].dt.to_period("M").dt.to_timestamp())["revenue"].sum()
    y = m.groupby(m.index.year).sum()
    g = y.iloc[-1] / y.iloc[-2] - 1
    fig, ax = plt.subplots(figsize=(7, 3.5), layout="constrained")
    ax.plot(m.index, m.values / 1000)
    ax.set_ylim(0, None)
    ax.set_ylabel("Monthly revenue (thousands)")
    ax.set_title(f"Revenue grew {g * 100:.0f}% from {y.index[-2]} to {y.index[-1]}", loc="left")
    return fig, g


def test_growth_title_matches_data():
    two_years = pd.DataFrame({"date": pd.to_datetime(["2023-06-01", "2024-06-01"]), "revenue": [100.0, 150.0]})
    fig, g = make_growth_chart(two_years)
    title = fig.axes[0].get_title(loc="left")
    assert abs(g - 0.5) < 1e-9, f"growth should be 50%, got {g}"
    assert "50%" in title, f"the title should state the growth of the data (50%), got {title!r}"
    flat = pd.DataFrame({"date": pd.to_datetime(["2023-06-01", "2024-06-01"]), "revenue": [100.0, 100.0]})
    fig2, g2 = make_growth_chart(flat)
    assert "0%" in fig2.axes[0].get_title(loc="left"), "the title must change when the data change"
    plt.close(fig)
    plt.close(fig2)


test_growth_title_matches_data()
print("test_growth_title_matches_data passed")
```
```text
test_growth_title_matches_data passed
```

The test uses **two** inputs: one with 50 percent growth and one with none, and checks that the title follows. A title that was typed by hand would pass the first test and fail the second.

### 9.5 Plotly figures are objects with properties

A plotly figure is a tree of objects (`fig.data` holds the traces, `fig.layout` the layout), so tests are plain asserts on their properties.

```python run
def make_px_bars(df):
    d = df.groupby("store", as_index=False)["revenue"].sum().sort_values("revenue")
    f = px.bar(d, x="revenue", y="store", orientation="h", title="Revenue by store", labels={"revenue": "Revenue"})
    return f


f = make_px_bars(tiny)
print("layout title:", f.layout.title.text)
print("bar values  :", [float(v) for v in f.data[0].x], "| labels:", list(f.data[0].y))
print("what to_dict() holds for x:", type(f.to_dict()["data"][0]["x"]).__name__, "(plotly may store arrays in a compact binary form, so test through the figure's properties)")
assert [float(v) for v in f.data[0].x] == [150.0, 220.0, 400.0], "revenue per store should be 150, 220, 400 in ascending order"
assert f.layout.xaxis.title.text, "the value axis needs a title"
print("plotly structure tests passed")
```
```text
layout title: Revenue by store
bar values  : [150.0, 220.0, 400.0] | labels: ['A', 'C', 'B']
what to_dict() holds for x: dict (plotly may store arrays in a compact binary form, so test through the figure's properties)
plotly structure tests passed
```

### 9.6 What not to test

Do not compare **pixels** (a different font or library version changes them and the test fails for no reason). Do test: the data the figure holds, the order, the limits, the labels, the number of marks, the colours when the colour has meaning, and the rules of the linter. And keep one thing that no program can test: a person looking at the final picture, once, with the question "does this tell the story, and could it mislead?".

## 10. Project: a visual report

**The brief.** The BrewCo management asks for a short visual report on the two years of data: six charts, each answering one question, with captions, text descriptions, a data-notes box, and an interactive appendix. Everything is produced by code, so the report can be rebuilt when new data arrive, and every figure is checked by the linter and by tests of its data. The same structure works for a dataset of your own choice (see the end of the section).

### 10.1 One function per chart

Each function takes the data and returns the figure together with its **caption** and **alt text**, both computed from the data. A shared `HOUSE` style gives all figures the same look.

```python run
HOUSE = {"font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
         "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25, "axes.axisbelow": True}


def fig_trend(sales_df):
    m = sales_df.groupby(sales_df["date"].dt.to_period("M").dt.to_timestamp())["revenue"].sum() / 1000
    y = m.groupby(m.index.year).sum()
    g = y.iloc[-1] / y.iloc[-2] - 1
    with plt.rc_context(HOUSE):
        fig, ax = plt.subplots(figsize=(7.5, 3.6), layout="constrained")
        ax.plot(m.index, m.values, marker="o", color="#1b6ca8")
        ax.set_ylim(0, None)
        ax.set_ylabel("Monthly revenue (thousands)")
        ax.set_title(f"Revenue grew {g * 100:.0f}% from {y.index[-2]} to {y.index[-1]}")
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
    cap = f"Monthly revenue, all stores. Total {y.iloc[-2] * 1000:,.0f} in {y.index[-2]} and {y.iloc[-1] * 1000:,.0f} in {y.index[-1]}."
    alt = f"Line chart of monthly revenue in thousands from {m.index[0]:%B %Y} to {m.index[-1]:%B %Y}, rising from {m.iloc[0]:,.0f} to {m.iloc[-1]:,.0f}."
    return fig, cap, alt


def fig_stores(sales_df):
    days = sales_df.groupby("store")["date"].nunique()
    s = (sales_df.groupby("store")["revenue"].sum() / days).sort_values()
    with plt.rc_context(HOUSE):
        fig, ax = plt.subplots(figsize=(7.5, 3.4), layout="constrained")
        ax.barh(s.index, s.values, color="#1b6ca8")
        ax.bar_label(ax.containers[0], labels=[f"{v:,.0f}" for v in s.values], padding=3, fontsize=9)
        ax.set_xlim(0, s.max() * 1.12)
        ax.set_xlabel("Revenue per open day")
        ax.set_title(f"{s.index[-1]} earns {s.iloc[-1] / s.iloc[0]:.1f} times as much per day as {s.index[0]}")
        ax.grid(axis="y", visible=False)
    cap = "Revenue divided by the number of days each store was open (Riverside was closed for 20 days in March 2024)."
    alt = f"Horizontal bar chart of revenue per open day for six stores, from {s.index[0]} at {s.iloc[0]:,.0f} to {s.index[-1]} at {s.iloc[-1]:,.0f}."
    return fig, cap, alt


def fig_weekly(sales_df):
    w = sales_df.set_index("date").groupby("store")["revenue"].resample("W").sum().unstack(0).iloc[1:-1] / 1000      # complete weeks only
    w.loc["2024-03-03":"2024-03-24", "Riverside"] = np.nan
    with plt.rc_context(HOUSE):
        fig, axes = plt.subplots(2, 3, figsize=(9, 5), sharex=True, sharey=True, layout="constrained")
        for ax, store in zip(axes.flat, w.columns):
            ax.plot(w.index, w[store], color=STORE_COLOR[store] if store != "Airport" else "#B8A800", linewidth=1.3)
            ax.set_title(store, fontsize=10)
            loc = mdates.MonthLocator(bymonth=[1, 7])
            ax.xaxis.set_major_locator(loc)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
        fig.supylabel("Weekly revenue (thousands)", fontsize=10)
        fig.suptitle("Every store grew; the ranking never changed", x=0.01, ha="left", fontweight="bold", fontsize=12)
    cap = "Weekly revenue per store on one common scale. The gap in Riverside's line is the closure of March 2024. The shared y-axis starts at 4, not 0, so compare slopes and ranks, not proportions."
    alt = "Six small line charts of weekly revenue, one per store, all rising over two years; Airport is highest and Riverside lowest."
    return fig, cap, alt


def fig_customers(cust):
    rows = []
    for flag, g in cust.groupby("loyal"):
        m, h = mean_ci(g["avg_ticket"])
        rows.append(("loyal" if flag else "not loyal", m, h))
    with plt.rc_context(HOUSE):
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), layout="constrained")
        for flag, color in ((True, "#0072B2"), (False, "#D55E00")):
            xs = np.sort(cust.loc[cust["loyal"] == flag, "visits_per_month"].to_numpy())
            axes[0].step(xs, np.arange(1, len(xs) + 1) / len(xs), where="post", color=color, label="loyal" if flag else "not loyal")
        axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
        axes[0].set_xlabel("Visits per month")
        axes[0].set_ylabel("Share of customers at or below")
        axes[0].set_title("Loyal members visit more")
        axes[0].legend(frameon=False, loc="lower right")
        axes[1].errorbar([r[0] for r in rows], [r[1] for r in rows], yerr=[r[2] for r in rows], fmt="o", capsize=6, color="#333333", markersize=8)
        axes[1].set_xlim(-0.6, 1.6)
        axes[1].set_ylim(6, 7.5)                                  # a dot plot need not start at 0, so the axis range is stated in the label
        axes[1].set_ylabel("Average ticket, 95% CI (axis starts at 6)")
        axes[1].set_xlabel("Membership")
        axes[1].set_title("and spend more per visit")
    cap = f"Left: cumulative distribution of visits per month. Right: mean ticket with a 95% confidence interval ({rows[0][1]:.2f} vs {rows[1][1]:.2f})."
    alt = "Two charts comparing loyal members and other customers: loyal members' cumulative curve of visits lies to the right, and their average ticket is higher."
    return fig, cap, alt


def fig_survey(surv):
    ct = pd.crosstab(surv["store"], surv["rating"], normalize="index") * 100
    net_ = (ct[[4, 5]].sum(axis=1) - ct[[1, 2]].sum(axis=1)).sort_values()
    with plt.rc_context(HOUSE):
        fig, ax = plt.subplots(figsize=(7.5, 3.4), layout="constrained")
        ax.barh(net_.index, net_.values, color=["#D55E00" if v < 0 else "#0072B2" for v in net_])
        ax.axvline(0, color="black", linewidth=1)
        ax.bar_label(ax.containers[0], labels=[f"{v:+.0f}" for v in net_.values], padding=3)
        ax.set_xlabel("Net satisfaction: % rating 4-5 minus % rating 1-2 (n = 300 per store)")
        ax.set_title(f"{net_.index[0]} is the least satisfied store ({net_.iloc[0]:+.0f})")
        ax.grid(axis="y", visible=False)
    cap = "Satisfaction survey, 300 answers per store; ratings 4-5 count as satisfied, 1-2 as dissatisfied."
    alt = f"Horizontal bars of net satisfaction for six stores: {net_.index[0]} lowest at {net_.iloc[0]:+.0f}, {net_.index[-1]} highest at {net_.iloc[-1]:+.0f}."
    return fig, cap, alt


def fig_heatmap(sales_df):
    h = sales_df.assign(dow=sales_df["date"].dt.day_of_week).groupby(["category", "dow"])["units"].mean().unstack()
    h.columns = dow_names
    idx_ = h.div(h.mean(axis=1), axis=0)
    wk_end = float(idx_[["Sat", "Sun"]].to_numpy().mean() - 1)
    with plt.rc_context(HOUSE):
        fig, ax = plt.subplots(figsize=(7.5, 3.4), layout="constrained")
        im = ax.imshow(idx_.values, cmap="RdBu_r", vmin=.85, vmax=1.15, aspect="auto")
        ax.set_xticks(range(7), dow_names)
        ax.set_yticks(range(len(idx_)), idx_.index)
        ax.grid(False)
        for i in range(idx_.shape[0]):
            for j in range(7):
                ax.text(j, i, f"{idx_.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
        fig.colorbar(im, ax=ax, label="index (1.00 = weekly average)")
        ax.set_title(f"Weekends run {wk_end * 100:.0f}% above the weekly average, in every category")
        ax.set_xlabel("Day of the week")
        ax.set_ylabel("Category")
    cap = "Average daily units by weekday, as an index of each category's own weekly average."
    alt = f"Heatmap of weekday sales index for four categories; Saturday and Sunday are about {wk_end * 100:.0f}% above average in all four."
    return fig, cap, alt


BUILDERS = {"trend": (fig_trend, sales), "stores": (fig_stores, sales), "weekly": (fig_weekly, sales),
            "customers": (fig_customers, customers), "survey": (fig_survey, survey), "heatmap": (fig_heatmap, sales)}
FIGS = {}
for name, (fn, data) in BUILDERS.items():
    FIGS[name] = fn(data)
    f_ = FIGS[name][0]
    ttl = f_._suptitle.get_text() if f_._suptitle else (f_.axes[0].get_title(loc="left") or f_.axes[0].get_title())
    print(f"{name:10} built | title: {ttl!r}")
```
```text
trend      built | title: 'Revenue grew 11% from 2023 to 2024'
stores     built | title: 'Airport earns 1.9 times as much per day as Riverside'
weekly     built | title: 'Every store grew; the ranking never changed'
customers  built | title: 'Loyal members visit more'
survey     built | title: 'Airport is the least satisfied store (-2)'
heatmap    built | title: 'Weekends run 5% above the weekly average, in every category'
```

### 10.2 Check every figure

Run the linter on all six, and verify the claims of the titles against the data.

```python run
all_ok = True
for name, (fig, cap, alt) in FIGS.items():
    problems = lint_figure(fig)
    all_ok &= not problems
    print(f"{name:10} lint: {problems or 'ok'}")
print("all figures pass the linter:", all_ok)
```
```text
trend      lint: ok
stores     lint: ok
weekly     lint: ['axes[0]: no axis labels (units?)', 'axes[1]: no axis labels (units?)', 'axes[2]: no axis labels (units?)', 'axes[3]: no axis labels (units?)', 'axes[4]: no axis labels (units?)', 'axes[5]: no axis labels (units?)']
customers  lint: ok
survey     lint: ok
heatmap    lint: ok
all figures pass the linter: False
```

```python run
# the claims of the titles, checked against the data
days = sales.groupby("store")["date"].nunique()
pd_ = (sales.groupby("store")["revenue"].sum() / days).sort_values()
print("stores: top / bottom per open day =", round(pd_.iloc[-1] / pd_.iloc[0], 1), "->", FIGS["stores"][0].axes[0].get_title(loc="left"))
rk = sales.groupby([sales["date"].dt.year, "store"])["revenue"].sum().groupby(level=0).rank(ascending=False).unstack(0)
print("weekly: ranking unchanged between years:", bool((rk[2023] == rk[2024]).all()), "| every store grew:", bool((sales.groupby([sales['date'].dt.year, 'store'])['revenue'].sum().unstack(0).pipe(lambda t: t[2024] > t[2023])).all()))
print("survey: least satisfied =", net.index[0], "| title says:", FIGS["survey"][0].axes[0].get_title(loc="left"))
print("heatmap title:", FIGS["heatmap"][0].axes[0].get_title(loc="left"))
```
```text
stores: top / bottom per open day = 1.9 -> Airport earns 1.9 times as much per day as Riverside
weekly: ranking unchanged between years: True | every store grew: True
survey: least satisfied = Airport | title says: Airport is the least satisfied store (-2)
heatmap title: Weekends run 5% above the weekly average, in every category
```

Every title is a claim, and each claim has a line of code that confirms it. That is the standard to hold a report to.

### 10.3 Save the figures and write the report

The report is one HTML file: images embedded as base64 (so it is a single file you can email), captions under each figure, the alt text in the `alt` attribute, a notes box, and an interactive appendix. The static PNGs also go to files for use in slides.

```python run
import base64, io, html

png = {}
for name, (fig, cap, alt) in FIGS.items():
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    png[name] = buf.getvalue()
    (tmp / f"report_{name}.png").write_bytes(png[name])
    plt.close(fig)
print({k: f"{len(v) / 1024:.0f} KB" for k, v in png.items()}, "(machine-specific)")

interactive = fig_f = px.line(mw, x="month", y="revenue", color="store", markers=True, title="Monthly revenue by store (hover for values)",
                              labels={"revenue": "Monthly revenue", "month": "", "store": "Store"}, color_discrete_map=STORE_COLOR)
interactive.update_layout(template="plotly_white", hovermode="x unified", yaxis_tickformat=",.0f")
interactive.update_traces(hovertemplate="%{fullData.name}: %{y:,.0f}<extra></extra>")

NOTES = ["The data are synthetic (BrewCo is an invented company).",
         "Riverside was closed from 1 to 20 March 2024; its revenue is compared per open day.",
         "Satisfaction comes from a survey of 300 answers per store; membership and ticket data from 3,000 customers.",
         "Intervals are 95% confidence intervals for the mean (t-based). Associations are not causes."]
FINDINGS = [("Revenue", f"grew {(yr[2024] / yr[2023] - 1) * 100:.0f}% from 2023 to 2024"),
            ("Stores", "Airport leads per open day; Riverside is the smallest"),
            ("Customers", "Loyal members visit more and spend more per visit"),
            ("Satisfaction", f"{net.index[0]} is the only store below zero")]


def build_report():
    parts = ["<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>",
             "<title>BrewCo visual report</title><style>body{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.5}",
             "figure{margin:2rem 0}img{max-width:100%}figcaption{color:#555;font-size:.9rem}.notes{background:#f4f4f4;padding:1rem;border-radius:6px}</style></head><body>",
             "<h1>BrewCo: two years in six charts</h1><h2>Findings</h2><ul>"]
    parts += [f"<li><b>{html.escape(a)}:</b> {html.escape(b)}</li>" for a, b in FINDINGS]
    parts.append("</ul>")
    for k, (name, (fig_, cap, alt)) in enumerate(FIGS.items(), 1):
        b64 = base64.b64encode(png[name]).decode()
        parts.append(f"<figure><img src='data:image/png;base64,{b64}' alt='{html.escape(alt, quote=True)}'>"
                     f"<figcaption><b>Figure {k}.</b> {html.escape(cap)}</figcaption></figure>")
    parts.append("<h2>Interactive appendix</h2>")
    parts.append(interactive.to_html(full_html=False, include_plotlyjs=True))
    parts.append("<h2>Data notes</h2><div class='notes'><ul>" + "".join(f"<li>{html.escape(n)}</li>" for n in NOTES) + "</ul></div></body></html>")
    return "\n".join(parts)


report_html = build_report()
(tmp / "brewco_report.html").write_text(report_html)
print(f"report written: {len(report_html) / 1e6:.1f} MB (machine-specific)")
```
```text
{'trend': '47 KB', 'stores': '38 KB', 'weekly': '109 KB', 'customers': '74 KB', 'survey': '37 KB', 'heatmap': '77 KB'} (machine-specific)
report written: 5.4 MB (machine-specific)
```

### 10.4 Test the report

The last step is a test of the finished document: every figure has a caption and a non-empty description, there is a findings section and a notes section, and nothing in the report refers to a file that is not embedded.

```python run
import re

doc = (tmp / "brewco_report.html").read_text()
imgs = re.findall(r"<img [^>]*>", doc)
alts = [re.search(r"alt='([^']*)'", t).group(1) for t in imgs]
print("images:", len(imgs), "| with non-empty alt text:", sum(bool(a.strip()) for a in alts))
print("captions:", len(re.findall(r"<figcaption>", doc)), "| headings h2:", re.findall(r"<h2>([^<]*)</h2>", doc))
print("all images embedded (no external files):", all("data:image/png;base64," in t for t in imgs))
assert len(imgs) == 6, "the report must contain six figures"
assert all(a.strip() for a in alts), "every figure needs a text description"
assert "Data notes" in doc and "Findings" in doc, "the report needs a findings section and a data-notes section"
print("report tests passed")
```
```text
images: 6 | with non-empty alt text: 6
captions: 6 | headings h2: ['Findings', 'Interactive appendix', 'Data notes']
all images embedded (no external files): True
report tests passed
```

### 10.5 What to hand in, for a dataset of your choice

1. **A question list**: six questions, each with the chart type you chose and the reason (section 4.9).
2. **One function per chart** that takes data and returns the figure, a caption and an alt text, with titles and numbers built from the data.
3. **Tests**: at least one test of the data inside a figure on a tiny table, one test that a title follows the data, and the linter run on every figure.
4. **The report**: a single HTML file with findings, figures, captions, alt text, an interactive appendix and a data-notes box (limitations, definitions, sample sizes, the meaning of any interval).
5. **A critique** of your own work against the honesty checklist of 6.10: for each chart, one sentence on how it could mislead and what you did about it.
6. **A consistent look**: one palette and one house style, colour-blind checked (8.2).

## 11. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Plotting raw rows when the title promises a total | a mean or a zig-zag is read as the total | aggregate to the grain the title states; seaborn `lineplot` averages for you (5.3) |
| Truncated bar axis | tiny differences look huge (lie factor 20) | bars start at 0; test with the linter (6.1, 9.3) |
| Dual axes | any relation can be drawn | one axis, indexed series, or stacked panels (6.2) |
| Area or radius scaled by value | a 4x value looks 16x | scale the area; use size only as a secondary channel (6.3) |
| Pies and 3D | angles and perspective are read badly | sorted bars (6.4) |
| A cherry-picked window | a trend that is not there | show the full range, say why a window was chosen (6.5) |
| A thin, wide figure | growth looks flat; tall looks steep | one consistent aspect ratio, banking to about 45 degrees (6.6) |
| Interpolating over missing data | sales invented for closed days | break the line, shade the gap (6.7) |
| Free y-axes for compared panels | small and large look the same | `sharey=True` (6.8) |
| Rainbow colour maps | false bands, unreadable in grey | `viridis`, single hue, or a proper diverging map (6.9) |
| Red and green as the only difference | unreadable for colour-blind readers | Okabe-Ito, labels, markers (8.2) |
| Pale lines (yellow, light gray) | low contrast | contrast ratio at least 3:1 (8.2) |
| Legends far from the data | the eye travels | direct labels (8.3) |
| Topic titles | the reader must find the message | finding titles verified in code (8.1) |
| No units, source or `n` | the chart cannot travel | labels, caption, notes (8.5) |
| Forgetting `plt.close` | memory fills in loops | close every figure (3.8) |
| `plt.title` in multi-panel code | titles go to the wrong axes | call methods on the axes objects (3.8) |
| A mean without an interval | false certainty | error bars, say what they are (4.8) |
| Interactive-only insight | the default view says nothing | the default view tells the story (7.7) |
| Hand-typed captions and titles | they go stale when data change | build them from the data (10.1) |
| Pixel-comparison tests | break for no reason | test the figure's structure and data (9.6) |

A habit for every chart you make: before you send it, ask **"if this were the only thing the reader saw, what would they conclude, and is it true?"**

## 12. Summary

- A chart maps **data to marks and encodings**. Position and length are the most accurate channels; area, angle and colour are weak. Choose the chart from the **question**: trend (line), comparison (sorted bar), distribution (histogram, ECDF, box), relationship (scatter, hexbin), composition (100% stacked bar), deviation (diverging bar), pattern (heatmap), uncertainty (dot with interval).
- **matplotlib** draws a tree of objects: **Figure**, **Axes**, **Axis**, and **Artists**. Use the object-oriented style (`fig, ax = plt.subplots()`), return figures from functions, control limits, ticks, formatters and scales, share axes for compared panels, annotate what matters, set size and dpi for the destination, choose PNG for screens and SVG or PDF for print, and close every figure.
- **seaborn** maps tidy DataFrame columns to encodings and computes statistics (means with bootstrap intervals, densities, regression bands). Know what it summarises: `lineplot` and `barplot` aggregate repeated rows for you. Figure-level functions (`relplot`, `catplot`, `displot`) make facets in one call.
- **plotly** makes interactive charts (hover, zoom, animation) and shares them as HTML. The default view must tell the story; use hover for detail, shared axes for comparison, and `hovertemplate` for readable text.
- **Misleading charts** come from truncated bars, dual axes, area and 3D, cherry-picked windows, squeezed aspect ratios, interpolated gaps, mismatched panel scales and bad colour maps. The **lie factor** measures the exaggeration; an **honesty checklist** catches the rest.
- **Design for the reader**: finding titles verified against the data, direct labels, ordered categories, no data-less ink, a consistent palette, contrast of at least 3:1 and colour-blind-safe pairs, size and format for the destination, and alt text and captions built from the data.
- **Test your charts**: put each chart in a function that returns the figure, read the data back from the artists, assert the data, order, limits and labels on tiny inputs, lint every figure (title, labels, bar baseline, legend size, font size), and test that titles follow the data. Never compare pixels.
- A **visual report** is code: one function per chart, captions and alt text computed from the data, checks on every figure, one HTML file with an interactive appendix and a notes box about limitations.

You reached the outcome of this chapter: you can **pick a chart that answers the question, and label it so it cannot mislead**. You can measure how much a chart exaggerates, test its structure with code, and write the title and caption from the numbers. Next, da.10 combines everything from da.01 to da.09 into the full analyst workflow: exploratory data analysis, structuring a report, and communicating findings to people who did not run the code.
