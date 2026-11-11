# Chapter 10 (DA): EDA, reporting and communication

You can now load data, clean it (da.05), define a metric precisely (da.06), query it (da.07), judge how sure you are (da.08), and draw an honest chart (da.09). Each of those is a skill. This chapter is the **job**: putting all of them together to answer a question that someone cares about, and handing over the answer in a form that someone else can act on.

Here is a scene that happens every week in every company. A manager says: "Churn is up. What is going on?" An analyst who has only skills opens a notebook, makes forty charts, finds six interesting things, and sends a long message that begins "I looked at the data and here are some observations". The manager reads the first line, does not know what to do, and puts it aside. An analyst who has the **job** does something different. They turn the vague worry into a precise question, list the possible explanations *before* looking, test each one, work out how much each explains, and then write one page that begins with the answer, says what to do, how much it is worth, and how sure they are.

By the end of this chapter you reach one outcome: **you can write a one-page finding that a manager can act on**. On the way you learn: **hypothesis-driven exploratory data analysis** (EDA), the discipline of looking at data with questions; **KPIs and metrics**, how to choose and define the numbers that a business steers by; the **communication flow** (question, analysis, finding, recommendation, limitations); **reports as code**, so that a finding can be rebuilt next month; and **Streamlit**, a Python library that turns an analysis into an interactive dashboard in a few dozen lines.

Prerequisites: da.09 (charts, and the habit of testing them) and da.06 (grain, metric definitions, reconciliation). We use da.08 (intervals, confounding) throughout: every claim in a finding needs its uncertainty.

> **Offline rule for this chapter.** pandas, NumPy, SciPy, statsmodels, matplotlib and Streamlit are installed in the course environment. No internet is needed. The dataset is **synthetic**, built in code with seeded random numbers: the company, its customers and the causes of its problems are invented. Because we built the world, we know the true causes, so at the end you can see whether the analysis found them. Every output block below was produced by running the code above it, in one session from top to bottom. **Versions, file sizes and temporary paths are machine-specific.** The Streamlit dashboard is tested *headlessly* with Streamlit's own test tool: no browser opens, and the test prints what the app would show. To see the app yourself, run `streamlit run app.py` on the saved file.

```python run
import sys, os, pathlib, tempfile, io, json, hashlib, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import scipy
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import streamlit as st

print("python     ", sys.version.split()[0])
print("pandas     ", pd.__version__)
print("numpy      ", np.__version__)
print("scipy      ", scipy.__version__)
print("statsmodels", sm.__version__)
print("streamlit  ", st.__version__)
```
```text
python      3.14.4
pandas      3.1.1
numpy       2.5.4
scipy       1.18.1
statsmodels 0.15.0
streamlit   1.67.0
```

Two setup lines: compact tables, and a temporary folder for every file we write.

```python run
pd.set_option("display.width", 115)
pd.set_option("display.max_columns", 14)
pd.set_option("display.float_format", "{:,.2f}".format)
_tmp = tempfile.TemporaryDirectory()
tmp = pathlib.Path(_tmp.name)
print("temp folder ready:", tmp.exists())
```
```text
temp folder ready: True
```

## Table of contents

1. [From data to decision](#1-from-data-to-decision)
2. [The case: FreshBox](#2-the-case-freshbox)
3. [KPIs and metrics](#3-kpis-and-metrics)
4. [Hypothesis-driven EDA](#4-hypothesis-driven-eda)
5. [Testing the hypotheses](#5-testing-the-hypotheses)
6. [Writing the finding](#6-writing-the-finding)
7. [Reports as code](#7-reports-as-code)
8. [Streamlit dashboards](#8-streamlit-dashboards)
9. [Project: a dashboard with a findings page](#9-project-a-dashboard-with-a-findings-page)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. From data to decision

### 1.1 The analyst's job

Data analysis has no value until it changes a decision. A decision is made by a person with limited time, who did not see your work, who must be able to say "yes, do it" or "no" and who will be asked "why?" by someone else. Everything you write is for that person. So the job has five steps, always in this order:

| Step | The question it answers | What you produce |
|---|---|---|
| **1. Question** | What exactly do we need to know, and what decision does it feed? | a precise question and the decision behind it |
| **2. Analysis** | What does the data say, and how sure are we? | tested hypotheses, with sizes and intervals |
| **3. Finding** | So what? What is the one thing to remember? | one sentence with a number |
| **4. Recommendation** | What should we do, who, by when, what will it gain? | an action with an owner and a range of impact |
| **5. Limitations** | What could make this wrong? | the honest limits: data, method, what you did not check |

Most weak reports skip step 1 (they answer a question nobody asked), blur steps 3 and 4 (they list observations without saying what to do), and hide step 5 (they leave the doubts out to look confident). This chapter gives you a method for each.

### 1.2 What "actionable" means

A finding is **actionable** when the reader can answer these without calling you.

1. **What is the claim?** One sentence, with a number: "Late deliveries raised churn by about 60 percent."
2. **How big is it, and how sure are we?** An estimate with an interval.
3. **What should we do?** A specific action, not "monitor the situation".
4. **Who does it and by when?** An owner and a date.
5. **What will it gain, and what will it cost?** A range, in the unit the business uses (money, customers).
6. **What could be wrong?** The two or three limits that matter.
7. **How will we know it worked?** The metric that will move, and by how much.

We will turn this list into a program (a **finding linter**, like the chart linter of da.09) so that a draft can be checked automatically.

### 1.3 Answer first

Business writing follows the **pyramid principle**: put the answer at the top, then the reasons, then the evidence. A reader who stops after the first two lines should still know what you found and what you recommend. Compare the two openings.

> *Version A (a story in the order you discovered it).* "I started by looking at overall churn by month, then I split by channel, then by plan, and then I noticed that something happened in September, so I looked at deliveries..."
>
> *Version B (the answer first; the numbers are only an illustration here, the real ones come in section 6).* "Monthly churn rose from 4.0 to 5.7 percent after September because late deliveries more than doubled. Restoring on-time delivery to 92 percent would bring most of it back. Recommendation: review the courier contract, owner and date named."

Version A is how you *thought*. Version B is how you must *write*. The path you took belongs in an appendix, not in the opening.

### 1.4 The one-page finding: a template

Every finding in this chapter follows one template; the sections are in the order a reader needs them.

```text
HEADLINE            one sentence: what changed, by how much, why
RECOMMENDATION      what to do, owner, date
IMPACT              the size of the gain, as a range, and the cost
EVIDENCE            two or three charts or numbers that prove the headline
CONFIDENCE          how sure we are, and why
LIMITATIONS         what this does not tell us
NEXT STEPS          what we will check next, and how we will measure success
```

We return to this template in section 6 and fill it with real numbers.

## 2. The case: FreshBox

### 2.1 The company and the worry

**FreshBox** is a synthetic meal-kit subscription company. Customers pay each week for a box of ingredients (a 2-meal plan at 599 rupees or a 3-meal plan at 849) and can cancel at any time. In the November review the head of operations says: **"Our churn jumped in the autumn. What happened, and what should we do?"** This is a vague worry, not a question. Our first job is to make it precise, and our second to list what could explain it.

The data factory is long; read the comments, which list the facts we planted. The point of simulating is that the **true causes are known to us and hidden from the analysis**, so at the end we can check whether the method found them.

```python run
WEEKS = pd.date_range("2023-01-02", "2024-12-30", freq="W-MON")           # 105 weeks, each starting on a Monday


def make_freshbox(seed=21, n=8000):
    rng = np.random.default_rng(seed)
    W = len(WEEKS)
    signup = rng.integers(0, 87, n)                                        # signup week index; none in the last 4 months
    paid_p = np.where(signup < 75, .35, .55)                               # TRUE CAUSE 3: more paid-ad customers after mid-2024
    channel = np.where(rng.random(n) < paid_p, "paid", np.where(rng.random(n) < .7, "organic", "referral"))
    plan = rng.choice(["2-meal", "3-meal"], n, p=[.55, .45])
    city = rng.choice(["Metro", "Large", "Small"], n, p=[.45, .35, .2])
    ch_mult = pd.Series(channel).map({"paid": 1.5, "organic": 1.0, "referral": 0.7}).to_numpy()   # paid customers churn faster
    sep_week = int((pd.Timestamp("2024-09-02") - WEEKS[0]).days / 7)       # TRUE CAUSE 1: late deliveries jump in September 2024
    hike_week = int((pd.Timestamp("2024-10-07") - WEEKS[0]).days / 7)      # TRUE CAUSE 2 (small): 3-meal price +10% from 7 Oct 2024
    alive = np.zeros(n, bool)
    churn_idx = np.full(n, -1)
    tenure = np.zeros(n, int)
    late_hist = np.zeros((n, 3), bool)                                     # a late box in the last 3 weeks raises the churn hazard
    rows = []
    for t in range(W):
        alive |= (signup == t)
        idx = np.flatnonzero(alive)
        if len(idx) == 0:
            continue
        late = rng.random(len(idx)) < (0.08 if t < sep_week else 0.20)     # 8% of boxes late, then 20%
        price = np.where(plan[idx] == "2-meal", 599, np.where(t >= hike_week, 934, 849))
        rows.append(pd.DataFrame({"customer_id": idx, "week": WEEKS[t], "tenure_wk": tenure[idx], "late": late, "price": price}))
        late_hist[idx] = np.column_stack([late_hist[idx][:, 1:], late])
        recent_late = late_hist[idx].any(axis=1)
        ten_mult = np.where(tenure[idx] < 8, 1.6, 1.0) * np.exp(-0.01 * np.minimum(tenure[idx], 60))   # new customers churn most
        hike = ((plan[idx] == "3-meal") & (t >= hike_week)).astype(float)
        hazard = 0.008 * ch_mult[idx] * ten_mult * np.exp(1.1 * recent_late + 0.15 * hike)            # weekly chance of leaving
        gone = rng.random(len(idx)) < hazard
        churn_idx[idx[gone]] = t
        alive[idx[gone]] = False
        tenure[idx] += 1
    panel = pd.concat(rows, ignore_index=True)
    cw = np.full(n, np.datetime64("NaT"), dtype="datetime64[ns]")
    cw[churn_idx >= 0] = WEEKS.values[churn_idx[churn_idx >= 0]]
    customers = pd.DataFrame({"customer_id": np.arange(n), "signup_week": WEEKS[signup], "channel": channel, "plan": plan,
                              "city": city, "last_week": pd.to_datetime(cw)})                         # last_week: the last active week; empty if still active
    return customers, panel


customers, panel = make_freshbox()
print("customers", customers.shape, "| grain: one row per customer")
print("panel    ", panel.shape, "| grain: one row per customer and active week")
print(customers.head(3).to_string(index=False))
print(panel.head(3).to_string(index=False))
```
```text
customers (8000, 6) | grain: one row per customer
panel     (337776, 5) | grain: one row per customer and active week
 customer_id signup_week  channel   plan  city  last_week
           0  2023-07-03  organic 2-meal Metro 2023-12-11
           1  2024-04-15 referral 3-meal Small        NaT
           2  2023-08-21     paid 3-meal Large 2023-10-09
 customer_id       week  tenure_wk  late  price
          47 2023-01-02          0 False    849
         195 2023-01-02          0 False    849
         231 2023-01-02          0 False    599
```

### 2.2 The first audit

Before any question about churn, the audit of da.05 and da.06: grain, keys, coverage, missing values, plausibility. In an analysis meant to be handed over, this is the first thing you check, because a problem found here is cheap, and the same problem found after the recommendation is expensive.

```python run
print("customer_id unique:", customers["customer_id"].is_unique)
print("panel key (customer_id, week) unique:", not panel.duplicated(["customer_id", "week"]).any())
print("panel customers all known:", bool(panel["customer_id"].isin(customers["customer_id"]).all()))
print("date range:", panel["week"].min().date(), "to", panel["week"].max().date(), "| weeks:", panel["week"].nunique())
print("customers who have left:", int(customers["last_week"].notna().sum()), "| still active:", int(customers["last_week"].isna().sum()))
print("missing values by column:")
print(customers.isna().sum().to_string())
```
```text
customer_id unique: True
panel key (customer_id, week) unique: True
panel customers all known: True
date range: 2023-01-02 to 2024-12-30 | weeks: 105
customers who have left: 3902 | still active: 4098
missing values by column:
customer_id       0
signup_week       0
channel           0
plan              0
city              0
last_week      4098
```

The only missing column is `last_week`, and its meaning matters: a missing value there is not an error, it means **the customer is still active**. Dropping those rows would delete every current customer and leave only the ones who left (survivorship, da.08). The rule from da.05 applies: ask *why* a value is missing before touching it.

Check the panel against the customer table: every customer's last panel week should equal `last_week` when they have left.

```python run
last_seen = panel.groupby("customer_id")["week"].max()
left = customers.dropna(subset=["last_week"]).set_index("customer_id")["last_week"]
print("customers who left whose last panel week equals last_week:", bool((last_seen.loc[left.index] == left).all()))
active = customers[customers["last_week"].isna()]
print("active customers whose last panel week is the final week of data:", bool((last_seen.loc[active["customer_id"]] == WEEKS[-1]).all()))
print("customers with fewer than 2 weeks of history:", int((panel.groupby("customer_id").size() < 2).sum()))
```
```text
customers who left whose last panel week equals last_week: True
active customers whose last panel week is the final week of data: True
customers with fewer than 2 weeks of history: 125
```

Both hold. We write the data dictionary once, because every later definition refers to it.

```python run
dictionary = pd.DataFrame([
    ("customers", "customer", "customer_id", "signup_week, channel, plan, city, last_week", "last_week is empty while the customer is active"),
    ("panel", "customer per active week", "customer_id + week", "tenure_wk, late, price", "one row per week the customer received (or was due) a box; the last row is the last active week"),
], columns=["table", "one row per", "key", "columns", "notes"])
print(dictionary.to_string(index=False))
```
```text
    table              one row per                key                                     columns                                                                                           notes
customers                 customer        customer_id signup_week, channel, plan, city, last_week                                                 last_week is empty while the customer is active
    panel customer per active week customer_id + week                      tenure_wk, late, price one row per week the customer received (or was due) a box; the last row is the last active week
```

## 3. KPIs and metrics

### 3.1 What a KPI is

A **metric** is any number you can compute. A **KPI** (key performance indicator) is a metric that the business has chosen to **steer by**: it is tied to a goal, has an owner, a target and a rule for what to do when it moves. A company can track hundreds of metrics, but only a handful are KPIs. The test of a KPI is a question: *if this number changed tomorrow, who would do something different?* If the answer is "nobody", it is a metric, not a KPI.

A good KPI has seven properties.

| Property | Meaning | Counter-example |
|---|---|---|
| **Tied to a decision or goal** | someone acts on it | "page views" for a subscription business |
| **Precisely defined** | numerator, denominator, date basis (da.06) | "engagement" with no definition |
| **Owned** | a person or team is responsible | a number nobody can change |
| **Comparable over time** | same definition every period | a definition that changed in July |
| **Normalised** | a rate, not a raw count, when the base grows | "number of cancellations" while the base doubles |
| **Timely** | available soon enough to act | quarterly churn reviewed once a year |
| **Hard to game** | improving the number means improving the business | "on-time rate" that couriers can edit |

### 3.2 Leading and lagging, vanity and guardrails

**Lagging** KPIs report outcomes after the fact (revenue, churn). **Leading** KPIs move first and predict them (late-delivery rate, support tickets, first-week activity). A good dashboard shows both: the lagging one tells you *whether* you are winning, the leading one tells you *early* when you are about to lose. **Vanity metrics** look impressive and drive no decision (total sign-ups ever, page views, followers); they only go up. A **guardrail** is a metric you refuse to hurt while you optimise another: if you cut delivery cost, the guardrail "on-time rate" must not fall. Finally **Goodhart's law**: when a measure becomes a target, it stops being a good measure. If couriers are paid for the on-time rate, they will find ways to mark boxes on time. Define KPIs with that incentive in mind, and audit them.

### 3.3 The KPI tree

KPIs are not independent: they form a tree in which each number is the product or sum of numbers below it. Writing the tree down shows where a change can come from, and it is the first tool of hypothesis-driven EDA.

```text
Weekly revenue
 = active subscribers  x  average price per box
      active subscribers (this week) = active last week + new customers - churned customers
          churned = opening actives x churn rate
              churn rate  <-  late-delivery rate (leading)
              churn rate  <-  customer mix (channel, plan, city, tenure)
              churn rate  <-  price changes
              churn rate  <-  season
      average price per box <- plan mix, price changes
```

The "churn" in the question lives in the middle of the tree. Its possible causes are the four branches under it: **delivery quality, customer mix, price, season**. That list is our hypothesis list (section 4).

### 3.4 Defining the KPIs

Following da.06, each KPI gets a written definition before any code. Here are the four that matter for the question.

| KPI | Definition | Date basis |
|---|---|---|
| **Opening actives** | customers who received a box in the first week of the month | first week of the month |
| **Monthly churn rate** | of the opening actives, the share whose last active week falls in the month | `last_week` in the month |
| **On-time rate** (leading) | share of boxes delivered on time, all active customer-weeks | `week` in the month |
| **Weekly revenue** | sum of `price` over the panel rows of the week | `week` |

A precision worth reading twice: customers who join and leave inside the same month are in **neither** the numerator nor the denominator of the churn rate, because they were not active at the start. The definition says so; a reader who computed it differently would get a slightly different number, and the written definition is how you settle it.

```python run
def monthly_kpis(customers, panel):
    """One row per month with the KPIs defined above."""
    p = panel.assign(month=panel["week"].dt.to_period("M"))
    first = p.groupby("month")["week"].min()                                          # first week present in each month
    opening = p[p["week"].isin(first.values)][["customer_id", "month"]]               # customers active in the first week
    opening = opening.merge(customers[["customer_id", "last_week"]], on="customer_id", how="left", validate="m:1")
    opening["churned"] = opening["last_week"].dt.to_period("M") == opening["month"]    # the last active week falls in this month
    out = opening.groupby("month").agg(opening_actives=("customer_id", "size"), churned=("churned", "sum"))
    out["churn_rate_pct"] = out["churned"] / out["opening_actives"] * 100
    out["on_time_pct"] = (1 - p.groupby("month")["late"].mean()) * 100
    out["weekly_revenue_k"] = p.groupby(["month", "week"])["price"].sum().groupby("month").mean() / 1000
    return out


kpi = monthly_kpis(customers, panel)
print(kpi.loc["2024-04":].round(2).to_string())
```
```text
         opening_actives  churned  churn_rate_pct  on_time_pct  weekly_revenue_k
month                                                                           
2024-04             4192      203            4.84        92.05          3,068.18
2024-05             4472      166            3.71        91.94          3,239.96
2024-06             4628      182            3.93        91.88          3,351.55
2024-07             4827      208            4.31        91.92          3,524.57
2024-08             5102      178            3.49        92.14          3,689.20
2024-09             5181      309            5.96        80.08          3,603.49
2024-10             4872      251            5.15        79.67          3,586.25
2024-11             4621      240            5.19        80.15          3,395.37
2024-12             4381      283            6.46        79.35          3,193.42
```

Read the table the way a manager would. Churn was between 3.5 and 4.8 percent a month until August, then jumped to 6 percent in September. The on-time rate fell from about 92 to about 80 percent in the same month. Two numbers moved at once: that is a lead, not yet an explanation. Part of any EDA is learning to say "these moved together" without yet saying "this caused that".

```python run
before = kpi.loc["2024-04":"2024-08"]
after = kpi.loc["2024-09":"2024-12"]
print(f"churn rate  Apr-Aug 2024: {before['churn_rate_pct'].mean():.2f}%   Sep-Dec 2024: {after['churn_rate_pct'].mean():.2f}%   change: {after['churn_rate_pct'].mean() - before['churn_rate_pct'].mean():+.2f} points")
print(f"on-time     Apr-Aug 2024: {before['on_time_pct'].mean():.1f}%   Sep-Dec 2024: {after['on_time_pct'].mean():.1f}%")
print(f"opening actives per month: {before['opening_actives'].mean():,.0f} before, {after['opening_actives'].mean():,.0f} after")
```
```text
churn rate  Apr-Aug 2024: 4.06%   Sep-Dec 2024: 5.69%   change: +1.64 points
on-time     Apr-Aug 2024: 92.0%   Sep-Dec 2024: 79.8%
opening actives per month: 4,644 before, 4,764 after
```

Note the third line: there are about as many opening actives before and after (about 4,600 against 4,800), so the jump is not a side effect of a bigger base. The precise question is now: **"Monthly churn rose from about 4.0 to about 5.7 percent in September to December 2024. Which of delivery quality, customer mix, price and season explains the rise, and how much does each contribute?"** That is a question one can answer, and the decision behind it is "where do we spend effort and money to bring churn back down".


## 4. Hypothesis-driven EDA

### 4.1 Two ways to explore

**Aimless EDA** opens the data and plots everything: every column against every other, in the hope that something looks interesting. It is easy to start and hard to finish, because there is no way to know when you are done. Worse, it produces dozens of comparisons, and by da.08 some will look significant by luck alone. The findings it gives are the kind that "do not replicate".

**Hypothesis-driven EDA** starts from the question and a list of possible explanations, written **before** looking at the evidence for them. Each hypothesis says what pattern would appear if it were true, and what pattern would **falsify** it. You then look for exactly those patterns. The work has an end (every hypothesis is supported, rejected or left open), and the findings have a structure a reader can follow.

The loop:

1. **Observe** a pattern or a worry (churn rose in September).
2. **Hypothesise**: list the candidate explanations from the KPI tree.
3. **Predict**: for each, write down what the data should show, and what would refute it.
4. **Test** with the smallest analysis that can refute it (with an interval, da.08).
5. **Update**: keep, reject, or refine; add new hypotheses that the results suggest.
6. **Log** everything you tried, including what failed.

The log is not paperwork. It keeps you honest about how many things you tried (the forking-paths problem of da.08), and it is the raw material of the appendix.

### 4.2 Look at the time profile first

Before cutting by segment, draw the thing that changed over time, with the possible cause next to it. We already have both KPIs; a two-panel chart puts them on one shared time axis (the alternative to a dual-axis chart in da.09).

```python run
fig, axes = plt.subplots(2, 1, figsize=(8, 5), sharex=True, layout="constrained")
x = kpi.index.to_timestamp()
axes[0].plot(x, kpi["churn_rate_pct"], marker="o", color="#D55E00")
axes[0].set_ylabel("Monthly churn (%)")
axes[0].set_ylim(0, None)
axes[0].set_title("Churn and on-time delivery changed in the same month", loc="left", fontweight="bold")
axes[1].plot(x, kpi["on_time_pct"], marker="o", color="#0072B2")
axes[1].set_ylabel("Boxes on time (%)")
axes[1].set_ylim(0, 100)
for ax in axes:
    ax.axvspan(pd.Timestamp("2024-09-01"), pd.Timestamp("2024-12-31"), color="gray", alpha=.12)
    ax.spines[["top", "right"]].set_visible(False)
fig.savefig(tmp / "overview.png", dpi=110)
print("axes:", len(fig.axes), "| lines per axes:", [len(a.lines) for a in fig.axes], "| title:", axes[0].get_title(loc="left"))
plt.close(fig)
print("on-time rate range before Sep 2024:", round(kpi.loc[:"2024-08", "on_time_pct"].min(), 1), "to", round(kpi.loc[:"2024-08", "on_time_pct"].max(), 1))
print("on-time rate after Sep 2024      :", round(kpi.loc["2024-09":, "on_time_pct"].min(), 1), "to", round(kpi.loc["2024-09":, "on_time_pct"].max(), 1))
print("churn rate range Jan-Aug 2024    :", round(kpi.loc["2024-01":"2024-08", "churn_rate_pct"].min(), 1), "to", round(kpi.loc["2024-01":"2024-08", "churn_rate_pct"].max(), 1))
print("churn rate range Sep-Dec 2024    :", round(kpi.loc["2024-09":, "churn_rate_pct"].min(), 1), "to", round(kpi.loc["2024-09":, "churn_rate_pct"].max(), 1))
```
```text
axes: 2 | lines per axes: [1, 1] | title: Churn and on-time delivery changed in the same month
on-time rate range before Sep 2024: 91.4 to 92.8
on-time rate after Sep 2024      : 79.3 to 80.1
churn rate range Jan-Aug 2024    : 3.5 to 4.8
churn rate range Sep-Dec 2024    : 5.2 to 6.5
```

The on-time rate was flat (about 92 percent) for twenty months and dropped by 12 points in a single month; churn rose in the same month. Look also at the left of the top panel, because a skeptical reader will: churn in early 2023 was *higher* than in the autumn of 2024 (5 to 8 percent). That is not a contradiction. At the start of 2023 the whole base consisted of recent sign-ups, and new customers churn two to three times as often as old ones (the tenure cut of 4.4 shows it). A fair comparison is between months with a similar kind of base, so we compare autumn 2024 with the months just before it, and we keep tenure in the analysis. The timing is a strong clue, and exactly what a lagged cause looks like. Remember da.08: two things moving together is not yet a cause. Customer mix, price and season could also have moved around then. So we write the hypotheses down.

### 4.3 The hypothesis list

| # | Hypothesis | If true, we should see | What would refute it |
|---|---|---|---|
| **H1** | Late deliveries drive customers away | customers with recent late boxes churn more than similar customers without; more late boxes, more churn (dose-response); the effect appears in every channel and city | no difference in churn between customers with and without late boxes, once tenure and channel are held equal |
| **H2** | The customer mix changed (more high-churn customers) | the share of paid-ad customers rose, they churn more, and holding the mix fixed removes part of the rise | the mix did not move, or fixing it removes nothing |
| **H3** | The 3-meal price increase (7 October) caused cancellations | the 3-meal plan churns more *after* the change than the 2-meal plan (which had no price change), compared with before | the 3-meal plan did not change relative to the 2-meal plan |
| **H4** | It is seasonal (autumn always has more churn) | the same rise appears in September to December 2023 | no rise last autumn |

Write such a table for every analysis. Notice that the predictions are checkable, the refutations are concrete, and H3 and H4 each have a **comparison group** (the 2-meal plan, last year) that guards against confounding. Also note an early inconsistency check: H3 cannot be the *whole* story, because the price change came in October and churn rose in September.

### 4.4 Cut by segment

A first cut by the obvious columns tells you where the rise is concentrated and whether the customer base changed. We use the opening actives of each month (the denominator of the churn KPI) with their attributes.

```python run
def opening_frame(customers, panel):
    """One row per customer and month in which the customer was active in the first week (the churn KPI's denominator)."""
    p = panel.assign(month=panel["week"].dt.to_period("M"))
    first = p.groupby("month")["week"].min()
    o = p[p["week"].isin(first.values)][["customer_id", "month", "tenure_wk"]]
    o = o.merge(customers[["customer_id", "channel", "plan", "city", "last_week"]], on="customer_id", how="left", validate="m:1")
    o["churned"] = o["last_week"].dt.to_period("M") == o["month"]
    o["tenure_band"] = pd.cut(o["tenure_wk"], [-1, 7, 25, 10_000], labels=["0-7 wk", "8-25 wk", "26+ wk"])
    return o


opening = opening_frame(customers, panel)
P_BEFORE, P_AFTER = (pd.Period("2024-04"), pd.Period("2024-08")), (pd.Period("2024-09"), pd.Period("2024-12"))
in_before = opening["month"].between(*P_BEFORE)
in_after = opening["month"].between(*P_AFTER)
print("rows:", len(opening), "| before:", int(in_before.sum()), "| after:", int(in_after.sum()))
print("overall churn: before", round(opening.loc[in_before, "churned"].mean() * 100, 2), "% | after", round(opening.loc[in_after, "churned"].mean() * 100, 2), "%")
```
```text
rows: 75545 | before: 23221 | after: 19055
overall churn: before 4.04 % | after 5.68 %
```

The rows are customer-months, so a customer who stayed five months appears five times: the right grain for a monthly rate (da.06). Now the cuts: for each attribute, the share of the base and the churn rate in the two periods.

```python run
def segment_table(o, dim):
    rows = []
    for name, mask in (("before", in_before), ("after", in_after)):
        g = o[mask].groupby(dim, observed=True)["churned"].agg(["size", "mean"])
        g.columns = [f"{name} n", f"{name} churn %"]
        g[f"{name} churn %"] *= 100
        g[f"{name} share %"] = g[f"{name} n"] / g[f"{name} n"].sum() * 100
        rows.append(g)
    t = pd.concat(rows, axis=1)
    t["change (points)"] = t["after churn %"] - t["before churn %"]
    return t[["before share %", "after share %", "before churn %", "after churn %", "change (points)"]]


for dim in ["channel", "plan", "city", "tenure_band"]:
    print(f"--- {dim} ---")
    print(segment_table(opening, dim).round(1).to_string())
```
```text
--- channel ---
          before share %  after share %  before churn %  after churn %  change (points)
channel                                                                                
organic            46.50          44.80            3.60           5.00             1.40
paid               30.90          32.60            5.60           8.00             2.40
referral           22.70          22.60            2.70           3.60             0.90
--- plan ---
        before share %  after share %  before churn %  after churn %  change (points)
plan                                                                                 
2-meal           54.30          54.60            4.00           5.30             1.20
3-meal           45.70          45.40            4.10           6.20             2.10
--- city ---
       before share %  after share %  before churn %  after churn %  change (points)
city                                                                                
Large           33.30          32.90            4.50           5.80             1.30
Metro           45.00          45.30            3.80           5.70             1.90
Small           21.60          21.70            3.80           5.50             1.70
--- tenure_band ---
             before share %  after share %  before churn %  after churn %  change (points)
tenure_band                                                                               
0-7 wk                15.20           3.90            7.70          12.20             4.50
8-25 wk               28.70          23.70            3.90           7.40             3.50
26+ wk                56.20          72.30            3.10           4.80             1.70
```

Read the four tables, hypothesis by hypothesis, without yet concluding.

- **Channel (H2).** Paid customers churn the most (5.6 percent before, 8.0 after), and their *share* of the base grew a little (30.9 to 32.6 percent). The mix did move, but only slightly.
- **Churn rose in every row of every table**: in all channels, both plans, all three cities and all tenure bands. A mix change alone cannot produce a rise inside every segment; it must be something that touched everyone. That points at H1 (a service problem) rather than H2.
- **Tenure.** New customers (0 to 7 weeks) churn most, and their share of the base **fell** (we stopped acquiring in August in this data): a shift towards older customers, who churn less. This works *against* the rise: it masks part of it.
- **Plan (H3).** The 3-meal plan rose by 2.1 points and the 2-meal plan, which had no price change, by 1.2: both rose, and the 3-meal plan a bit more. That is a first hint of a price effect, to be tested properly in 5.4.

### 4.5 Mix against rate: how much of the change is which?

When an overall rate changes, two different things can be responsible: the **rate within each segment** changed, or the **mix of segments** changed. The decomposition is exact:

```text
overall rate = sum over segments of (segment share x segment rate)
change = sum of (change in share  x  average rate)     <- mix effect
       + sum of (average share  x  change in rate)     <- rate effect
```

Using averages of the before and after values makes the two parts add to the total change exactly. This is the tool for da.06's Simpson's paradox in practice.

```python run
def mix_rate_decomposition(o, dim):
    b, a = o[in_before], o[in_after]
    sb, sa = b[dim].value_counts(normalize=True), a[dim].value_counts(normalize=True)
    rb, ra = b.groupby(dim, observed=True)["churned"].mean(), a.groupby(dim, observed=True)["churned"].mean()
    keys = sb.index
    mix = float(((sa[keys] - sb[keys]) * (rb[keys] + ra[keys]) / 2).sum()) * 100
    rate = float((((ra[keys] - rb[keys])) * (sa[keys] + sb[keys]) / 2).sum()) * 100
    total = (a["churned"].mean() - b["churned"].mean()) * 100
    return mix, rate, total


rows = []
for dim in ["channel", "plan", "city", "tenure_band"]:
    mix, rate, total = mix_rate_decomposition(opening, dim)
    assert abs(mix + rate - total) < 1e-9, "the two effects must add up to the total change"
    rows.append({"dimension": dim, "mix effect (points)": mix, "rate effect (points)": rate, "total change": total})
print(pd.DataFrame(rows).round(2).to_string(index=False))
```
```text
  dimension  mix effect (points)  rate effect (points)  total change
    channel                 0.05                  1.60          1.65
       plan                -0.00                  1.65          1.65
       city                -0.00                  1.65          1.65
tenure_band                -0.76                  2.41          1.65
```

Every row adds up to the same total (about +1.6 points), and the **rate effect dominates** for each dimension. The mix effect is small for channel (positive: the paid share rose), roughly zero for plan and city, and **negative for tenure** (the base got older). So changes in the mix of customers explain little of the rise; the churn rate rose *inside* the segments. This does not close H2 entirely (the channel mix effect is positive and we will quantify it), but it reorders the work: the main explanation must be found in something that affected all customers equally.

> **Predict the output.** If the true cause were a pure mix shift (more paid customers, whose churn rate is constant), what would the rate effect and the mix effect of the **channel** decomposition look like?

<details><summary>Answer</summary>

The rate effect would be near zero (each channel's own churn rate would be unchanged) and the mix effect would carry the whole change. In our data it is the other way round: the channel rate effect is +1.60 points and the mix effect only +0.05. The decomposition therefore *rejects* "it is only a mix shift" and keeps "something raised churn within each channel".

</details>

### 4.6 Season and the base year

Before testing H1, a cheap check of H4 with the same tool: compare the same months of the year before. Last year's autumn is the **comparison group** for season.

```python run
b23 = opening["month"].between(pd.Period("2023-04"), pd.Period("2023-08"))
a23 = opening["month"].between(pd.Period("2023-09"), pd.Period("2023-12"))
for label, m in (("Apr-Aug 2023", b23), ("Sep-Dec 2023", a23), ("Apr-Aug 2024", in_before), ("Sep-Dec 2024", in_after)):
    k, n = int(opening.loc[m, "churned"].sum()), int(m.sum())
    ci = stats.binomtest(k, n).proportion_ci(0.95, method="wilson")
    print(f"{label}: churn {k / n * 100:5.2f}%  ({k} of {n}), 95% CI {ci.low * 100:.2f} to {ci.high * 100:.2f}")
```
```text
Apr-Aug 2023: churn  5.71%  (502 of 8797), 95% CI 5.24 to 6.21
Sep-Dec 2023: churn  4.83%  (567 of 11730), 95% CI 4.46 to 5.24
Apr-Aug 2024: churn  4.04%  (937 of 23221), 95% CI 3.79 to 4.30
Sep-Dec 2024: churn  5.68%  (1083 of 19055), 95% CI 5.36 to 6.02
```

In 2023 the autumn rate was, if anything, **lower** than the summer rate (4.8 against 5.7 percent), while in 2024 the autumn interval sits well above the summer one. So H4 is not supported: there is no seasonal rise to explain the 2024 jump. The base was smaller in 2023, so the 2023 intervals are wider, and we note that as a caveat (one year is a weak seasonal baseline).

## 5. Testing the hypotheses

### 5.1 The analysis table

For individual-level questions we need the customer-week panel with a flag for the week in which the customer leaves, and the history of late deliveries.

```python run
pn = panel.merge(customers[["customer_id", "channel", "plan", "city", "last_week"]], on="customer_id", how="left", validate="m:1")
pn = pn.sort_values(["customer_id", "week"]).reset_index(drop=True)
pn["churn_now"] = pn["week"] == pn["last_week"]                                    # the customer's last active week
roll = pn.groupby("customer_id")["late"].rolling(3, min_periods=1)
pn["late_in_3"] = roll.sum().reset_index(level=0, drop=True).to_numpy()             # late boxes in this and the previous 2 weeks
pn["late_recent"] = pn["late_in_3"] > 0
pn["tenure_band"] = pd.cut(pn["tenure_wk"], [-1, 7, 25, 10_000], labels=["0-7 wk", "8-25 wk", "26+ wk"])
pn["post"] = pn["week"] >= "2024-09-02"
pn["hike"] = (pn["plan"] == "3-meal") & (pn["week"] >= "2024-10-07")
print(pn.shape, "| churn events:", int(pn["churn_now"].sum()), "| weekly churn rate:", f"{pn['churn_now'].mean() * 1000:.1f} per 1,000 customer-weeks")
print("share of customer-weeks with a late box in the last 3 weeks: before Sep 2024", f"{pn.loc[~pn['post'], 'late_recent'].mean() * 100:.0f}%", "| after", f"{pn.loc[pn['post'], 'late_recent'].mean() * 100:.0f}%")
```
```text
(337776, 15) | churn events: 3902 | weekly churn rate: 11.6 per 1,000 customer-weeks
share of customer-weeks with a late box in the last 3 weeks: before Sep 2024 21% | after 47%
```

The grain is a customer-week, and `churn_now` marks the last week. About half of the customer-weeks since September have had a late box in the last three weeks, against about a fifth before.

### 5.2 H1: do late deliveries lead to churn?

The simplest test compares the weekly churn rate of customer-weeks **with** and **without** a recent late box. To compare like with like, we first check that lateness is not related to customer type (if couriers were late more often for new customers, it would be confounded with tenure).

```python run
bal = pd.DataFrame({
    "channel": pn.groupby("channel")["late"].mean(),
}).T
print("late-box rate by channel:", (pn.groupby("channel")["late"].mean() * 100).round(1).to_dict())
print("late-box rate by plan   :", (pn.groupby("plan")["late"].mean() * 100).round(1).to_dict())
print("late-box rate by city   :", (pn.groupby("city")["late"].mean() * 100).round(1).to_dict())
print("late-box rate by tenure :", (pn.groupby("tenure_band", observed=True)["late"].mean() * 100).round(1).to_dict())
```
```text
late-box rate by channel: {'organic': 11.0, 'paid': 11.2, 'referral': 11.0}
late-box rate by plan   : {'2-meal': 11.0, '3-meal': 11.2}
late-box rate by city   : {'Large': 11.1, 'Metro': 11.1, 'Small': 11.0}
late-box rate by tenure : {'0-7 wk': 8.5, '8-25 wk': 10.1, '26+ wk': 12.6}
```

Lateness is the same (about 11 percent) for every channel, plan and city: in this company it is a property of the courier network, not of who the customer is. The tenure rows differ (8.5 to 12.6 percent), but for a reason that has nothing to do with the customers: long-tenure weeks are concentrated after September, when lateness was higher everywhere. That is a **time confound**, and it is why the model in 5.3 holds the period and the tenure fixed together. That makes the comparison of late against not-late fairer than usual (the kind of assumption you would check with the operations team in real life). Now the rates:

```python run
def rate_ratio(e1, n1, e0, n0):
    rr = (e1 / n1) / (e0 / n0)
    se = np.sqrt(1 / e1 - 1 / n1 + 1 / e0 - 1 / n0)
    return rr, rr * np.exp(-1.96 * se), rr * np.exp(1.96 * se)


rows = []
for label, sub in (("all weeks", pn), ("Apr-Aug 2024 only", pn[(pn["week"] >= "2024-04-01") & (pn["week"] < "2024-09-02")]),
                   ("Sep-Dec 2024 only", pn[pn["post"]])):
    g = sub.groupby("late_recent")["churn_now"].agg(["sum", "size"])
    rr, lo, hi = rate_ratio(g.loc[True, "sum"], g.loc[True, "size"], g.loc[False, "sum"], g.loc[False, "size"])
    rows.append({"sample": label, "per 1,000 with late box": g.loc[True, "sum"] / g.loc[True, "size"] * 1000,
                 "per 1,000 without": g.loc[False, "sum"] / g.loc[False, "size"] * 1000, "rate ratio": rr, "CI low": lo, "CI high": hi})
print(pd.DataFrame(rows).round(2).to_string(index=False))
```
```text
           sample  per 1,000 with late box  per 1,000 without  rate ratio  CI low  CI high
        all weeks                    21.17               7.82        2.71    2.54     2.88
Apr-Aug 2024 only                    19.18               6.95        2.76    2.44     3.12
Sep-Dec 2024 only                    19.67               6.83        2.88    2.52     3.29
```

In every sample, customers with a late box in the last three weeks leave at about **2.7 to 2.9 times** the weekly rate of those without (the interval is far above 1 and the ratio is stable across the two periods). The ratio is similar before and after September, which means the *effect of a late box* did not change; what changed is **how many customers got late boxes**. That is the pattern H1 predicts, and exactly the pattern a mix-shift or price story would not produce.

A **dose-response** check: if lateness drives churn, more late boxes should mean more churn.

```python run
dose = pn.groupby("late_in_3")["churn_now"].agg(["sum", "size"])
dose["per 1,000 customer-weeks"] = dose["sum"] / dose["size"] * 1000
lo_hi = [stats.binomtest(int(r["sum"]), int(r["size"])).proportion_ci(0.95, method="wilson") for _, r in dose.iterrows()]
dose["CI low"] = [c.low * 1000 for c in lo_hi]
dose["CI high"] = [c.high * 1000 for c in lo_hi]
print(dose.round(2).to_string())
```
```text
            sum    size  per 1,000 customer-weeks  CI low  CI high
late_in_3                                                         
0.00       1905  243463                      7.82    7.48     8.18
1.00       1726   81871                     21.08   20.12    22.09
2.00        255   11704                     21.79   19.30    24.59
3.00         16     738                     21.68   13.39    34.93
```

Here the data do **not** give the textbook gradient. The weekly churn rate jumps from 7.8 per 1,000 with no late box to about 21 with one, and then stays at about 21 for two and three late boxes (the intervals overlap). The effect behaves like a **switch** ("has the customer had a bad experience recently?"), not like a dial. A graded dose-response would have been stronger evidence of a cause, and its absence is worth reporting honestly: it does not refute H1 (one bad box may be enough to make a customer reconsider), but it is a point we list under limitations. The other supports (a clear jump, a stable ratio, perfect timing, no confounding by customer type) remain.

### 5.3 Holding other things equal: a model

The comparison above ignores tenure, channel and the other factors. A **discrete-time hazard model** estimates the chance of leaving in a given week as a function of everything at once: logistic regression on the customer-week table, with standard errors that allow for repeated rows of the same customer (**cluster-robust** by customer).

```python run
def design(df):
    X = pd.DataFrame({
        "late_recent": df["late_recent"].astype(float),
        "hike": df["hike"].astype(float),
        "post": df["post"].astype(float),
        "paid": (df["channel"] == "paid").astype(float),
        "referral": (df["channel"] == "referral").astype(float),
        "plan_3meal": (df["plan"] == "3-meal").astype(float),
        "city_large": (df["city"] == "Large").astype(float),
        "city_small": (df["city"] == "Small").astype(float),
        "ten_8_25": (df["tenure_band"] == "8-25 wk").astype(float),
        "ten_26plus": (df["tenure_band"] == "26+ wk").astype(float),
    }, index=df.index)
    return sm.add_constant(X, has_constant="add")


X = design(pn)
y = pn["churn_now"].astype(float)
fit = sm.GLM(y, X, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": pn["customer_id"]})
ci = fit.conf_int()
res = pd.DataFrame({"odds ratio": np.exp(fit.params), "CI low": np.exp(ci[0]), "CI high": np.exp(ci[1]), "p": fit.pvalues}).drop(index="const")
print(res.round(3).to_string())
```
```text
             odds ratio  CI low  CI high    p
late_recent        2.90    2.71     3.09 0.00
hike               1.33    1.16     1.52 0.00
post               1.01    0.92     1.11 0.84
paid               1.51    1.41     1.62 0.00
referral           0.70    0.64     0.77 0.00
plan_3meal         0.97    0.91     1.04 0.45
city_large         1.08    1.00     1.16 0.04
city_small         0.98    0.90     1.06 0.60
ten_8_25           0.57    0.53     0.62 0.00
ten_26plus         0.41    0.38     0.45 0.00
```

Read the odds ratios (an odds ratio of 1 means no effect; for a rare event like weekly churn, it is close to a rate ratio).

- **`late_recent`**: 2.9 (interval 2.7 to 3.1): a recent late box nearly triples the weekly churn odds, **after** holding channel, plan, city, tenure, the price change and the September period equal. This confirms H1 and matches the planted effect (an odds ratio of e^1.1 = 3.0).
- **`post`** (the period from September, for anything else that changed): close to 1, interval including 1: once lateness is in the model, **nothing else unexplained** changed in September. The model is not missing a major cause.
- **`hike`** (the price increase on the 3-meal plan): an odds ratio of 1.33 (interval 1.16 to 1.52): the price rise does appear to have increased churn on the 3-meal plan, by roughly a third in relative terms, though the interval is wide.
- **`paid`**: about 1.5 (more churn than organic), **`referral`** about 0.7 (less): the channel effects, as expected.
- **Tenure**: older customers churn less than new ones.

### 5.4 H3: the price change as a natural experiment

The price change applied only to the 3-meal plan. The 2-meal plan is a **comparison group** that saw everything else the same. A **difference in differences** compares the change in the 3-meal plan's churn (after against before 7 October) with the change in the 2-meal plan's churn over the same dates. The comparison removes anything that hit both plans equally (like the delivery problem). Its key assumption is that, without the price change, the two plans would have moved in parallel.

```python run
w = pn[(pn["week"] >= "2024-09-02")]
w = w.assign(after_hike=w["week"] >= "2024-10-07")
cells = w.groupby(["plan", "after_hike"])["churn_now"].agg(["sum", "size"])
cells["rate_per_1000"] = cells["sum"] / cells["size"] * 1000
cells["var"] = cells["rate_per_1000"] / 1000 * (1 - cells["rate_per_1000"] / 1000) / cells["size"] * 1e6
print(cells.round(2).to_string())
r = cells["rate_per_1000"]
did = (r[("3-meal", True)] - r[("3-meal", False)]) - (r[("2-meal", True)] - r[("2-meal", False)])
se = np.sqrt(cells["var"].sum())
print(f"\ndifference in differences: {did:+.2f} per 1,000 customer-weeks, 95% CI {did - 1.96 * se:+.2f} to {did + 1.96 * se:+.2f}")
base_3 = r[("3-meal", False)]
print(f"as a share of the 3-meal plan's rate before the change ({base_3:.1f}): {did / base_3 * 100:+.0f}%  (CI {(did - 1.96 * se) / base_3 * 100:+.0f}% to {(did + 1.96 * se) / base_3 * 100:+.0f}%)")
```
```text
                   sum   size  rate_per_1000  var
plan   after_hike                                
2-meal False       171  13720          12.46 0.90
       True        376  32140          11.70 0.36
3-meal False       138  11542          11.96 1.02
       True        398  26383          15.09 0.56

difference in differences: +3.89 per 1,000 customer-weeks, 95% CI +0.59 to +7.20
as a share of the 3-meal plan's rate before the change (12.0): +33%  (CI +5% to +60%)
```

The difference in differences is **+3.9 weekly cancellations per 1,000 customer-weeks** (95 percent interval +0.6 to +7.2), which is about a third more cancellations on the 3-meal plan than it would have had (interval +5 to +60 percent). The interval excludes zero, so there is evidence of a price effect, but it is a wide interval: the data cannot say whether the effect is closer to 5 percent or 60 percent. It agrees with the model's odds ratio for `hike` (1.33). Remember the assumption: the 2-meal plan stands in for "what would have happened to the 3-meal plan without the price change". The verdict on H3: **a real but secondary effect**. It cannot explain the September rise (the change came a month later), but it adds to the autumn churn from October on.

### 5.5 How much does each cause contribute?

A finding needs sizes. We can ask a **counterfactual** question of the model: *what would the autumn churn have been if each cause had stayed at its summer level?* Taking the causes away one at a time, the drop each time is its contribution. The steps: (1) late boxes as frequent as in the summer, (2) no price change, (3) the summer customer mix (channel and tenure), (4) no "September" shift. For each, we recompute the model's average predicted weekly churn, and convert it to a monthly rate: `monthly = 1 - (1 - weekly)^(52/12)`.

```python run
sub_b = pn[(pn["week"] >= "2024-04-01") & (pn["week"] < "2024-09-02")]
sub_a = pn[pn["post"]]
cell_cols = ["late_recent", "hike", "post", "channel", "plan", "city", "tenure_band"]
cells_a = sub_a.groupby(cell_cols, observed=True).size().rename("n").reset_index()
cells_b = sub_b.groupby(cell_cols, observed=True).size().rename("n").reset_index()
Xa, Xb = design(cells_a), design(cells_b)
q_before = sub_b["late_recent"].mean()                      # share of customer-weeks with a recent late box in the summer
q_after = sub_a["late_recent"].mean()
mix_cols = ["channel", "tenure_band"]
share_b = sub_b.groupby(mix_cols, observed=True).size() / len(sub_b)
share_a = sub_a.groupby(mix_cols, observed=True).size() / len(sub_a)


def monthly(h):
    return 1 - (1 - h) ** (52 / 12)


def scenarios(beta):
    """Average weekly churn in the autumn under cumulative counterfactuals (a function of the coefficient vector)."""
    def avg(X, w):
        p = 1 / (1 + np.exp(-(X.to_numpy() @ beta)))
        return float((p * w).sum() / w.sum())
    w0 = cells_a["n"].to_numpy(float)
    out = {"autumn, as it was": avg(Xa, w0)}
    wl = w0 * np.where(cells_a["late_recent"], q_before / q_after, (1 - q_before) / (1 - q_after))          # lateness at the summer level
    out["... late boxes at summer level"] = avg(Xa, wl)
    Xh = Xa.copy(); Xh["hike"] = 0.0
    out["... and no price change"] = avg(Xh, wl)
    key = list(zip(cells_a["channel"], cells_a["tenure_band"]))
    ratio = np.array([share_b.get(k, 0) / share_a.get(k, np.nan) for k in key])
    wm = wl * ratio
    out["... and the summer customer mix"] = avg(Xh, wm)
    Xp = Xh.copy(); Xp["post"] = 0.0
    out["... and no September shift"] = avg(Xp, wm)
    return out


best = scenarios(fit.params.to_numpy())
base_week = float(sub_b["churn_now"].mean())
tbl = pd.DataFrame({"weekly churn per 1,000": {k: v * 1000 for k, v in best.items()}})
tbl["monthly churn %"] = [monthly(v) * 100 for v in best.values()]
tbl.loc["summer (Apr-Aug), observed"] = [base_week * 1000, monthly(base_week) * 100]
print(tbl.round(2).to_string())
```
```text
                                 weekly churn per 1,000  monthly churn %
autumn, as it was                                 12.93             5.48
... late boxes at summer level                     9.64             4.11
... and no price change                            8.79             3.75
... and the summer customer mix                   10.19             4.34
... and no September shift                        10.09             4.30
summer (Apr-Aug), observed                         9.60             4.09
```

Read the table from top to bottom: the first row is the autumn as the model reproduces it (about 5.5 percent a month). Each following row removes one more cause. Late boxes at the summer level removes by far the biggest step; the price change removes a smaller step; the summer customer mix removes a step *with the opposite sign* (the autumn base is older, which lowers churn, so restoring the summer mix raises it from 3.75 to 4.34); the final row, with the September shift also removed, lands at 4.30 percent, close to the observed summer rate of 4.09: the model has accounted for nearly the whole rise. To attach uncertainty to the contributions, we repeat the calculation for many coefficient vectors drawn from the model's estimated uncertainty (a **parametric bootstrap**).

```python run
rng = np.random.default_rng(5)
draws = rng.multivariate_normal(fit.params.to_numpy(), fit.cov_params().to_numpy(), size=600)
contrib = []
for beta in draws:
    s = scenarios(beta)
    v = [monthly(x) * 100 for x in s.values()]
    contrib.append([v[0] - v[1], v[1] - v[2], v[2] - v[3], v[3] - v[4], v[4] - monthly(base_week) * 100, v[0] - monthly(base_week) * 100])
contrib = pd.DataFrame(contrib, columns=["late deliveries", "price change", "customer mix", "September shift", "left unexplained", "observed rise (model)"])
summary = pd.DataFrame({"estimate": contrib.median(), "CI low": contrib.quantile(.025), "CI high": contrib.quantile(.975)})
summary["share of the rise %"] = summary["estimate"] / summary.loc["observed rise (model)", "estimate"] * 100
print(summary.round(2).to_string())
```
```text
                       estimate  CI low  CI high  share of the rise %
late deliveries            1.37    1.27     1.48                98.57
price change               0.36    0.18     0.55                26.11
customer mix              -0.59   -0.68    -0.50               -42.30
September shift            0.05   -0.35     0.43                 3.62
left unexplained           0.21    0.05     0.38                15.15
observed rise (model)      1.39    1.09     1.73               100.00
```

The result, in monthly churn points: **late deliveries account for almost the entire rise** (1.4 of 1.4 points, with an interval from 1.3 to 1.5); the **price change** adds a smaller, uncertain amount (about 0.4 points, interval 0.2 to 0.6); the **customer mix** works the other way (about −0.6 points: the base got older, which masks part of the rise); the **September shift** is near zero and a small remainder is left unexplained. The shares are medians over the simulated draws, so they add up to about 100 percent only approximately, and a single share can exceed 100 or fall below 0 because contributions can have opposite signs. Two cautions: the contributions depend a little on the order in which causes are removed (with interactions, a different order gives slightly different numbers), and the weekly model's rise (1.4 points) is measured on customer-weeks, while the KPI table's 1.6 uses opening actives, a different denominator. Now compare with what we planted: the late-delivery jump from 8 to 20 percent was the main cause, the price effect was small, and the paid share rose slightly. The analysis found them in the right order and of about the right sizes, **without being told**.

### 5.6 The evidence table

The last step of the analysis is a table a reader can scan: one row per hypothesis, with the test, the result with its uncertainty, and a verdict.

```python run
late_c = summary.loc["late deliveries"]
evidence = pd.DataFrame([
    ("H1 late deliveries", "rate ratio, dose-response, hazard model", f"odds ratio {np.exp(fit.params['late_recent']):.1f}; explains {late_c['estimate']:.1f} of {summary.loc['observed rise (model)', 'estimate']:.1f} points", "supported (main cause)"),
    ("H2 customer mix", "mix/rate decomposition, counterfactual", f"channel mix effect +0.05 points; the older base works against the rise ({summary.loc['customer mix', 'estimate']:+.2f} points)", "does not explain the rise"),
    ("H3 price change", "difference in differences, model", f"{did:+.2f} per 1,000 customer-weeks (CI {did - 1.96 * se:+.2f} to {did + 1.96 * se:+.2f}); about {summary.loc['price change', 'estimate']:.1f} points of churn", "supported but secondary; cannot explain September"),
    ("H4 season", "same months, previous year", "autumn 2023 churn was lower than summer 2023 (4.8% vs 5.7%)", "rejected"),
], columns=["hypothesis", "test", "result", "verdict"])
print(evidence.to_string(index=False))
```
```text
        hypothesis                                    test                                                                                result                                           verdict
H1 late deliveries rate ratio, dose-response, hazard model                                            odds ratio 2.9; explains 1.4 of 1.4 points                            supported (main cause)
   H2 customer mix  mix/rate decomposition, counterfactual channel mix effect +0.05 points; the older base works against the rise (-0.59 points)                         does not explain the rise
   H3 price change        difference in differences, model         +3.89 per 1,000 customer-weeks (CI +0.59 to +7.20); about 0.4 points of churn supported but secondary; cannot explain September
         H4 season              same months, previous year                           autumn 2023 churn was lower than summer 2023 (4.8% vs 5.7%)                                          rejected
```

This table is the spine of the written finding in section 6: the **headline** comes from the first row, the **secondary action** from the third, the **limitations** from the doubts attached to all four, and the **appendix** from the remaining two. Keep the log of everything else you tried. Here it would list the segment cuts of 4.4 and the 2023 comparison; in a real project it would also list dead ends.


## 6. Writing the finding

### 6.1 From the evidence table to a page

The analysis ends with an evidence table. A manager does not want the table; they want what it **means for a decision**. The step from one to the other is writing, and it follows rules.

**The headline** is one sentence with four parts: *what changed*, *by how much* (from X to Y, with the unit), *when*, and *why*. "Churn is up" is a topic. "Monthly churn rose from 4.0 to 5.7 percent in September to December 2024, almost entirely because late deliveries more than doubled" is a headline.

**The recommendation** names an action, an owner and a date. "We should look into delivery" fails all three. **The impact** is a *range* in the business's units (customers, rupees), with the cost beside it; a single figure claims precision the data cannot support (da.08). **Confidence** is a statement about the evidence ("strong for the main cause, weaker for the price effect"), in the vocabulary of da.08 ("consistent with", "suggests", "we estimate"), never "proves". **Limitations** are the two or three doubts that a reasonable reader would raise anyway: say them first, before they do.

### 6.2 Compute the numbers once, in one place

Every number in the finding comes from a dictionary filled by code. This is the rule of the chapter: **no number is typed by hand in the text.** When the data refresh, the text follows, and a reader can trace any figure back to the line that produced it.

```python run
price_after = float(pn.loc[pn["post"], "price"].mean())
open_after = float(kpi.loc["2024-09":"2024-12", "opening_actives"].mean())
late_est, late_lo, late_hi = (float(summary.loc["late deliveries", c]) for c in ("estimate", "CI low", "CI high"))
stay_months = 1 / (monthly(base_week))                                      # expected months a customer stays at the summer churn rate
saved = lambda pts: pts / 100 * open_after                                  # customers kept per month if churn drops by `pts` points
R = {
    "churn_before": float(opening.loc[in_before, "churned"].mean() * 100),
    "churn_after": float(opening.loc[in_after, "churned"].mean() * 100),
    "ontime_before": float(kpi.loc["2024-04":"2024-08", "on_time_pct"].mean()),
    "ontime_after": float(kpi.loc["2024-09":"2024-12", "on_time_pct"].mean()),
    "late_pts": late_est, "late_pts_lo": late_lo, "late_pts_hi": late_hi,
    "saved": saved(late_est), "saved_lo": saved(late_lo), "saved_hi": saved(late_hi),
    "price_after": price_after,
    "rr_late": float(np.exp(fit.params["late_recent"])),
    "rr_lo": float(np.exp(ci.loc["late_recent", 0])), "rr_hi": float(np.exp(ci.loc["late_recent", 1])),
    "hike_ratio": float(np.exp(fit.params["hike"])), "price_pts": float(summary.loc["price change", "estimate"]),
    "did_pct": float(did / base_3 * 100), "did_lo": float((did - 1.96 * se) / base_3 * 100), "did_hi": float((did + 1.96 * se) / base_3 * 100),
    "mix_pts": float(summary.loc["customer mix", "estimate"]),
}
R["weekly_rev_at_risk"] = R["saved"] * R["price_after"]                                   # weekly revenue of one month's saved customers
R["weekly_rev_lo"], R["weekly_rev_hi"] = R["saved_lo"] * price_after, R["saved_hi"] * price_after
R["lifetime_rev"] = R["weekly_rev_at_risk"] * 52 / 12 * stay_months                       # revenue those customers bring over their stay
print(pd.Series(R).round(2).to_string())
```
```text
churn_before                 4.04
churn_after                  5.68
ontime_before               91.98
ontime_after                79.81
late_pts                     1.37
late_pts_lo                  1.27
late_pts_hi                  1.48
saved                       65.18
saved_lo                    60.30
saved_hi                    70.53
price_after                738.93
rr_late                      2.90
rr_lo                        2.71
rr_hi                        3.09
hike_ratio                   1.33
price_pts                    0.36
did_pct                     32.57
did_lo                       4.92
did_hi                      60.21
mix_pts                     -0.59
weekly_rev_at_risk      48,159.72
weekly_rev_lo           44,558.51
weekly_rev_hi           52,119.67
lifetime_rev         5,097,970.03
```

Look at what the numbers say in business terms. The late deliveries added about 1.4 points to the monthly churn rate: with about 4,800 opening actives that is **roughly 65 customers a month** (the interval 60 to 71) who would have stayed. At an average of about 740 rupees a week per box, one month's worth of lost customers is **about 48,000 rupees of weekly revenue**, and if they stayed as long as customers typically do (about 24 months at the summer churn rate) they would bring over 5 million rupees. That is the size of what is at stake, in the unit a manager uses.

### 6.3 The finding as an object

Instead of writing the finding as free text, we represent it as a **structure** with the template's sections. That makes it checkable and renderable.

```python run
from dataclasses import dataclass, field
import re


@dataclass
class Finding:
    headline: str
    recommendations: list            # each: {"action": ..., "owner": ..., "by": ...}
    impact: str
    evidence: list                   # each: a sentence with a number
    confidence: str
    limitations: list
    next_steps: list
    figures: list = field(default_factory=list)      # file names of charts

    def render_markdown(self):
        lines = ["# " + self.headline, "", "### Recommendation"]
        lines += [f"- **{r['action']}** (owner: {r['owner']}; by {r['by']})" for r in self.recommendations]
        lines += ["", "### Impact", self.impact, "", "### Evidence"] + [f"- {e}" for e in self.evidence]
        lines += ["", "### Confidence", self.confidence, "", "### Limitations"] + [f"- {l}" for l in self.limitations]
        lines += ["", "### Next steps"] + [f"- {n}" for n in self.next_steps]
        return "\n".join(lines)


def make_finding(R):
    return Finding(
        headline=(f"Monthly churn rose from {R['churn_before']:.1f}% to {R['churn_after']:.1f}% in Sep-Dec 2024, almost entirely because "
                  f"on-time delivery fell from {R['ontime_before']:.0f}% to {R['ontime_after']:.0f}%"),
        recommendations=[
            {"action": f"Fix delivery reliability: restore the on-time rate to {R['ontime_before']:.0f}% (review the courier contract first)", "owner": "Head of Operations", "by": "31 January 2025"},
            {"action": "Pause the 3-meal price rise in other markets until it is tested against a control group", "owner": "Head of Pricing", "by": "15 January 2025"},
        ],
        impact=(f"Each month of delay costs about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f}), "
                f"about {R['weekly_rev_at_risk'] / 1000:.0f},000 rupees of weekly revenue (range {R['weekly_rev_lo'] / 1000:.0f},000 to {R['weekly_rev_hi'] / 1000:.0f},000). "
                f"The cost of the fix is not yet known; it pays back if it is below that revenue."),
        evidence=[
            f"Customers with a late box in the last 3 weeks leave {R['rr_late']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f}), holding channel, plan, city and tenure equal.",
            f"The rise in churn is {R['late_pts']:.1f} points (95% CI {R['late_pts_lo']:.1f} to {R['late_pts_hi']:.1f}) attributable to late boxes, nearly all of the observed rise.",
            f"The 3-meal price increase added about {R['price_pts']:.1f} points (the 3-meal churn rose {R['did_pct']:.0f}% relative to the 2-meal plan, 95% CI {R['did_lo']:.0f}% to {R['did_hi']:.0f}%).",
            "Customer mix and season do not explain the rise: autumn 2023 churn was lower than summer 2023, and the older customer base lowered churn."],
        confidence="High for late deliveries as the main cause (timing, size, a stable rate ratio and balance across customer types agree). Moderate for the price effect (a wide interval, one comparison group).",
        limitations=["Observational data: customers were not randomly assigned late boxes, although lateness did not depend on customer type.",
                     "The effect looks like a switch (any recent late box), not a gradient; we do not know whether one late box or its handling drives the exit.",
                     "The price estimate uses the 2-meal plan as a control and covers only eleven weeks after the change."],
        next_steps=["Operations to split late boxes by courier and city this month.",
                    "Run the next price change as a randomised test on part of the base.",
                    f"Success measure: monthly churn back to {R['churn_before']:.0f}-{R['churn_before'] + 0.5:.0f}% within three months of the fix."],
        figures=["overview.png"])


finding = make_finding(R)
md = finding.render_markdown()
print(md)
print("\nwords:", len(md.split()))
```
```text
# Monthly churn rose from 4.0% to 5.7% in Sep-Dec 2024, almost entirely because on-time delivery fell from 92% to 80%

### Recommendation
- **Fix delivery reliability: restore the on-time rate to 92% (review the courier contract first)** (owner: Head of Operations; by 31 January 2025)
- **Pause the 3-meal price rise in other markets until it is tested against a control group** (owner: Head of Pricing; by 15 January 2025)

### Impact
Each month of delay costs about 65 customers (range 60 to 71), about 48,000 rupees of weekly revenue (range 45,000 to 52,000). The cost of the fix is not yet known; it pays back if it is below that revenue.

### Evidence
- Customers with a late box in the last 3 weeks leave 2.9 times as often (95% CI 2.7 to 3.1), holding channel, plan, city and tenure equal.
- The rise in churn is 1.4 points (95% CI 1.3 to 1.5) attributable to late boxes, nearly all of the observed rise.
- The 3-meal price increase added about 0.4 points (the 3-meal churn rose 33% relative to the 2-meal plan, 95% CI 5% to 60%).
- Customer mix and season do not explain the rise: autumn 2023 churn was lower than summer 2023, and the older customer base lowered churn.

### Confidence
High for late deliveries as the main cause (timing, size, a stable rate ratio and balance across customer types agree). Moderate for the price effect (a wide interval, one comparison group).

### Limitations
- Observational data: customers were not randomly assigned late boxes, although lateness did not depend on customer type.
- The effect looks like a switch (any recent late box), not a gradient; we do not know whether one late box or its handling drives the exit.
- The price estimate uses the 2-meal plan as a control and covers only eleven weeks after the change.

### Next steps
- Operations to split late boxes by courier and city this month.
- Run the next price change as a randomised test on part of the base.
- Success measure: monthly churn back to 4-5% within three months of the fix.

words: 359
```

Read it as the manager would. The first line gives the answer. The second block says what to do, who does it and by when. The impact is in customers and rupees, with a range. The evidence is four sentences, each with a number and its interval. The confidence line separates what is solid from what is weaker. The limitations name what a skeptic would ask. The next steps include a **success measure**, so that in three months someone can say whether the action worked.

### 6.4 A finding linter

The chart linter of da.09 checked structure. The same idea works for writing: a few mechanical rules catch the common failures, so that a human reviewer can spend their attention on the judgement. Our linter implements the checklist of section 1.2.

```python run
VAGUE = ["monitor the situation", "further analysis", "look into", "it seems", "some observations", "as can be seen", "interesting"]


def lint_finding(f, max_words=400):
    issues = []
    h = f.headline
    if not re.search(r"\d", h):
        issues.append("headline has no number")
    if not re.search(r"\b(from|to|than|against|vs)\b|%", h):
        issues.append("headline gives no comparison (from X to Y)")
    if len(h.split()) > 40:
        issues.append(f"headline is {len(h.split())} words (more than 40)")
    if not f.recommendations:
        issues.append("no recommendation")
    for i, r in enumerate(f.recommendations):
        if not r.get("owner"):
            issues.append(f"recommendation {i + 1} has no owner")
        if not re.search(r"\d{1,2} \w+ \d{4}|\d{4}-\d{2}-\d{2}", str(r.get("by", ""))):
            issues.append(f"recommendation {i + 1} has no date")
    if not re.search(r"\d.*\b(to|between|-)\b.*\d|\brange\b", f.impact):
        issues.append("impact is a point, not a range")
    if not re.search(r"\b(customers|rupees|%|points)\b", f.impact):
        issues.append("impact is not in business units")
    if len(f.evidence) < 2 or not all(re.search(r"\d", e) for e in f.evidence):
        issues.append("evidence needs at least two items, each with a number")
    if not any(re.search(r"CI|interval|range", e) for e in f.evidence):
        issues.append("no evidence item carries its uncertainty")
    if not f.confidence.strip():
        issues.append("no statement of confidence")
    if len(f.limitations) < 2:
        issues.append("fewer than two limitations")
    if not any(re.search(r"success|measure|%", n) for n in f.next_steps):
        issues.append("no success measure in the next steps")
    text = f.render_markdown().lower()
    for phrase in VAGUE:
        if phrase in text:
            issues.append(f"vague phrase: {phrase!r}")
    if len(text.split()) > max_words:
        issues.append(f"{len(text.split())} words: too long for one page (max {max_words})")
    return issues


print("our finding:", lint_finding(finding) or "no problems")
```
```text
our finding: no problems
```

The finding passes. Now a typical weak draft, the way analysts often write on a first attempt:

```python run
weak = Finding(
    headline="Some observations about churn and deliveries",
    recommendations=[{"action": "Monitor the situation and look into delivery", "owner": "", "by": "soon"}],
    impact="Churn is a problem for revenue.",
    evidence=["Churn went up.", "Deliveries were late."],
    confidence="",
    limitations=["The data might be incomplete."],
    next_steps=["Further analysis."])
for issue in lint_finding(weak):
    print(" -", issue)
```
```text
 - headline has no number
 - headline gives no comparison (from X to Y)
 - recommendation 1 has no owner
 - recommendation 1 has no date
 - impact is a point, not a range
 - impact is not in business units
 - evidence needs at least two items, each with a number
 - no evidence item carries its uncertainty
 - no statement of confidence
 - fewer than two limitations
 - no success measure in the next steps
 - vague phrase: 'monitor the situation'
 - vague phrase: 'further analysis'
 - vague phrase: 'look into'
 - vague phrase: 'some observations'
```

Every problem a reader would feel is named: no number or comparison in the headline, no owner or date, a point instead of a range, no uncertainty, a single limitation, no success measure, and vague phrases. A linter cannot tell you whether the headline is *true* or the recommendation *wise* (that is your job, and the evidence table is the test), but it stops the draft that cannot be acted on.

### 6.5 Figures for the page

A finding uses **two or three** figures, each answering one of its claims. Here: the time profile (already drawn in 4.2) and the contribution of each cause with its interval. Both are built by functions and checked, as in da.09.

```python run
def fig_contributions(summary):
    s = summary.drop(index=["observed rise (model)", "left unexplained"]).sort_values("estimate")
    fig, ax = plt.subplots(figsize=(7, 3.2), layout="constrained")
    colors = ["#D55E00" if v > 0 else "#0072B2" for v in s["estimate"]]
    ax.barh(s.index, s["estimate"], color=colors)
    ax.errorbar(s["estimate"], range(len(s)), xerr=[s["estimate"] - s["CI low"], s["CI high"] - s["estimate"]], fmt="none", ecolor="black", capsize=4)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Contribution to the rise in monthly churn (percentage points, 95% interval)")
    ax.set_title(f"Late deliveries explain {s.loc['late deliveries', 'estimate']:.1f} of the {summary.loc['observed rise (model)', 'estimate']:.1f}-point rise", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    return fig


fig = fig_contributions(summary)
fig.savefig(tmp / "contributions.png", dpi=110)
ax = fig.axes[0]
print("title:", ax.get_title(loc="left"))
print("bars:", len(ax.patches), "| labels:", [t.get_text() for t in ax.get_yticklabels()])
plt.close(fig)
finding.figures = ["overview.png", "contributions.png"]
```
```text
title: Late deliveries explain 1.4 of the 1.4-point rise
bars: 4 | labels: ['customer mix', 'September shift', 'price change', 'late deliveries']
```

### 6.6 Render the page

The page is a single HTML file: the headline, the recommendation, the impact, the figures with captions, the evidence, the confidence and the limitations. Managers read it in a browser or print it to PDF.

```python run
import base64, html


def render_html(f, source_note):
    def img(name, alt):
        b64 = base64.b64encode((tmp / name).read_bytes()).decode()
        return f"<img src='data:image/png;base64,{b64}' alt='{html.escape(alt, quote=True)}' style='max-width:100%'>"
    alts = {"overview.png": "Two line charts over time: monthly churn jumps in September 2024 while the on-time delivery rate drops from 92 to 80 percent.",
            "contributions.png": "Horizontal bars of the contribution of each cause to the rise in churn: late deliveries are the largest, price smaller, customer mix negative."}
    p = ["<!doctype html><html lang='en'><head><meta charset='utf-8'><title>FreshBox churn: finding</title>",
         "<style>body{font-family:sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem;line-height:1.5}h1{font-size:1.5rem}.box{background:#f4f4f4;padding:.8rem 1rem;border-radius:6px}small{color:#555}</style></head><body>",
         f"<h1>{html.escape(f.headline)}</h1>", "<div class='box'><b>Recommendation</b><ul>"]
    p += [f"<li>{html.escape(r['action'])} <small>(owner: {html.escape(r['owner'])}; by {html.escape(r['by'])})</small></li>" for r in f.recommendations]
    p += ["</ul></div>", f"<p><b>Impact.</b> {html.escape(f.impact)}</p>"]
    p += [f"<figure>{img(n, alts.get(n, n))}</figure>" for n in f.figures]
    p += ["<h2>Evidence</h2><ul>"] + [f"<li>{html.escape(e)}</li>" for e in f.evidence] + ["</ul>"]
    p += [f"<h2>Confidence</h2><p>{html.escape(f.confidence)}</p><h2>Limitations</h2><ul>"] + [f"<li>{html.escape(l)}</li>" for l in f.limitations] + ["</ul>"]
    p += ["<h2>Next steps</h2><ul>"] + [f"<li>{html.escape(n)}</li>" for n in f.next_steps] + ["</ul>", f"<p><small>{html.escape(source_note)}</small></p></body></html>"]
    return "\n".join(p)


page = render_html(finding, "Data: FreshBox customer and weekly panel, 2023-01-02 to 2024-12-30 (synthetic). Analysis: hypothesis tests and hazard model, section 5.")
(tmp / "finding.html").write_text(page)
(tmp / "finding.md").write_text(finding.render_markdown())
words = len(re.sub(r"<[^>]+>", " ", re.sub(r"<img[^>]*>", " ", page)).split())
print(f"page written: {len(page) / 1024:.0f} KB (machine-specific) | words on the page: {words} | reading time: about {words / 200:.0f} minutes")
```
```text
page written: 97 KB (machine-specific) | words on the page: 365 | reading time: about 2 minutes
```

A page of about 360 words is a two-minute read. That is the right size: a reader who needs more can open the appendix (the evidence table and the log), but the decision must not depend on it.

### 6.7 Different readers, same numbers

The same finding is delivered in different sizes: a **three-line message** for a chat channel, a **one-page** for the manager, an **appendix** for the analyst who will check it. All are generated from `R`, so they cannot disagree.

```python run
def short_message(R):
    return (f"Churn is up ({R['churn_before']:.1f}% to {R['churn_after']:.1f}%) and late deliveries are the main cause "
            f"(on-time {R['ontime_before']:.0f}% to {R['ontime_after']:.0f}%). Fixing delivery would keep about {R['saved']:.0f} customers a month. "
            f"Decision needed: courier review, owner Operations, by 31 January.")


m = short_message(R)
print(m)
print("\nwords:", len(m.split()))
```
```text
Churn is up (4.0% to 5.7%) and late deliveries are the main cause (on-time 92% to 80%). Fixing delivery would keep about 65 customers a month. Decision needed: courier review, owner Operations, by 31 January.

words: 35
```

### 6.8 Writing rules

| Do | Do not |
|---|---|
| Put the answer in the first line | Tell the story in the order you discovered it |
| Give every number a comparison ("from 4.0% to 5.7%") | Quote a number alone |
| Use ranges and say the confidence level | Quote a point estimate as certain |
| Name an action, an owner and a date | Write "monitor the situation" |
| State the limits yourself | Hide the doubts and hope nobody asks |
| Use the units of the business (customers, rupees) | Use statistical units (odds ratios) in the headline |
| Say how success will be measured | Leave the next review without a test |
| Use "suggests", "is consistent with", "we estimate" for observational results | Use "proves" or "caused" without an experiment |
| Generate the text from the numbers | Type numbers by hand |

## 7. Reports as code

### 7.1 Why rebuild by code

A finding is not written once. The same question returns every month ("is the problem still there?") and the numbers change. If the analysis lives in a spreadsheet with hand-copied numbers, each update is a day of work and a new chance for a typo. If it is **code**, an update is one command, and the code is the documentation of exactly what was done (da.06's "definition in code").

A report built by code has five stages, which are separate functions:

```text
load data  ->  check data  ->  compute numbers  ->  write text and figures  ->  check the report
```

and one rule: **the only way a number reaches the page is through the dictionary of computed numbers.**

### 7.2 A light analysis that can be re-run for any date

The full model of section 5 takes seconds and is the basis of the confidence statement. For a monthly refresh a **lighter** version is useful: the same KPIs and a transparent estimate of the effect of late deliveries, from the rate ratio and the change in how often customers had a late box. We check that it agrees with the full model.

```python run
def quick_summary(customers, panel, as_of):
    """The headline numbers using only data up to `as_of`, complete months only."""
    as_of = pd.Timestamp(as_of)
    pnl = panel[panel["week"] <= as_of]
    cus = customers.assign(last_week=customers["last_week"].where(customers["last_week"] <= as_of))      # churn after as_of is not yet known
    last_month = as_of.to_period("M") - 1                                                                  # the last COMPLETE month
    k = monthly_kpis(cus, pnl[pnl["week"].dt.to_period("M") <= last_month])
    before = k.loc["2024-04":"2024-08"]
    after = k.loc["2024-09":last_month]
    pp = pn[(pn["week"] <= as_of) & pn["post"]]
    g = pp.groupby("late_recent")["churn_now"].agg(["sum", "size"])
    h1, h0 = g.loc[True, "sum"] / g.loc[True, "size"], g.loc[False, "sum"] / g.loc[False, "size"]
    q_b = pn.loc[(pn["week"] >= "2024-04-01") & (pn["week"] < "2024-09-02"), "late_recent"].mean()
    q_a = pp["late_recent"].mean()
    excess_pts = (q_a - q_b) * (h1 - h0) * 52 / 12 * 100                      # extra monthly churn points from more late boxes
    return {"as_of": str(as_of.date()), "months_after": len(after), "churn_before": float(before["churn_rate_pct"].mean()),
            "churn_after": float(after["churn_rate_pct"].mean()), "ontime_before": float(before["on_time_pct"].mean()),
            "ontime_after": float(after["on_time_pct"].mean()), "rate_ratio": float(h1 / h0), "late_pts": float(excess_pts),
            "saved": float(excess_pts / 100 * after["opening_actives"].mean())}


full = quick_summary(customers, panel, "2025-01-06")
print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in full.items()})
print(f"compare with the full model: late contribution {R['late_pts']:.2f} points (model) vs {full['late_pts']:.2f} (quick); customers {R['saved']:.0f} vs {full['saved']:.0f}")
```
```text
{'as_of': '2025-01-06', 'months_after': 4, 'churn_before': 4.06, 'churn_after': 5.69, 'ontime_before': 91.98, 'ontime_after': 79.81, 'rate_ratio': 2.88, 'late_pts': 1.44, 'saved': 68.4}
compare with the full model: late contribution 1.37 points (model) vs 1.44 (quick); customers 65 vs 68
```

The two ways of measuring agree closely (1.37 points in the model and 1.44 in the quick calculation; 65 and 70 customers a month). When a simple method and a sophisticated one give the same answer, the answer is far more believable. This is the same "second engine" habit as in da.07. Now re-run the whole thing as of a **different date** and see the text follow:

```python run
for as_of in ("2024-10-28", "2024-12-02", "2025-01-06"):
    s = quick_summary(customers, panel, as_of)
    print(f"as of {s['as_of']} ({s['months_after']} complete month(s) after the change): churn {s['churn_before']:.1f}% -> {s['churn_after']:.1f}%, "
          f"on-time {s['ontime_before']:.0f}% -> {s['ontime_after']:.0f}%, about {s['saved']:.0f} customers a month attributable to late boxes")
```
```text
as of 2024-10-28 (1 complete month(s) after the change): churn 4.1% -> 6.0%, on-time 92% -> 80%, about 79 customers a month attributable to late boxes
as of 2024-12-02 (3 complete month(s) after the change): churn 4.1% -> 5.4%, on-time 92% -> 80%, about 72 customers a month attributable to late boxes
as of 2025-01-06 (4 complete month(s) after the change): churn 4.1% -> 5.7%, on-time 92% -> 80%, about 68 customers a month attributable to late boxes
```

With only September complete (the last complete month before 28 October), the first line already shows the problem; with December complete, three more months confirm it, and the numbers settle at the ones in the finding (5.7 percent, about 70 customers by this quick method). The same function, run monthly, is a **monitor**: when `churn_after` moves outside a threshold it can send the alert. The text of the finding can be rebuilt from `quick_summary` plus the model-based interval. Notice that we never typed a number.

### 7.3 Provenance: what was this built from?

A report that cannot say which data it used is untraceable. Put a fingerprint of the input and the code version in the footer, and test that the same input gives the same output.

```python run
def fingerprint(df):
    h = hashlib.sha256(pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes()).hexdigest()
    return h[:10]


prov = {"data_rows": {"customers": len(customers), "panel": len(panel)},
        "data_fingerprint": {"customers": fingerprint(customers.fillna(pd.Timestamp("1970-01-01"))), "panel": fingerprint(panel)},
        "data_from": str(panel["week"].min().date()), "data_to": str(panel["week"].max().date()), "analysis_date": "2025-01-06"}
print(json.dumps(prov, indent=1))
again = fingerprint(panel)
print("same data, same fingerprint:", again == prov["data_fingerprint"]["panel"])
changed = panel.copy()
changed.loc[0, "price"] += 1
print("one value changed, fingerprint changes:", fingerprint(changed) != prov["data_fingerprint"]["panel"])
```
```text
{
 "data_rows": {
  "customers": 8000,
  "panel": 337776
 },
 "data_fingerprint": {
  "customers": "ed165cda35",
  "panel": "fbd0c9b12a"
 },
 "data_from": "2023-01-02",
 "data_to": "2024-12-30",
 "analysis_date": "2025-01-06"
}
same data, same fingerprint: True
one value changed, fingerprint changes: True
```

Print the provenance at the bottom of every report ("data fingerprint 3f9a..., 337,776 rows, to 30 December 2024"). Months later, when two people have different numbers, the first question is "same fingerprint?", and it settles half the arguments in a second.

### 7.4 Checks on the finished report

The report itself needs tests, as the chart did in da.09: the numbers in the text must equal the numbers computed, every figure must exist, and nothing may be left from a template.

```python run
def check_report(md_text, R, figures_dir):
    problems = []
    for key, fmt in (("churn_before", "{:.1f}%"), ("churn_after", "{:.1f}%")):
        if fmt.format(R[key]) not in md_text:
            problems.append(f"{key} = {fmt.format(R[key])} does not appear in the text")
    if "{" in md_text or "}" in md_text or "TODO" in md_text:
        problems.append("unfilled template placeholder or TODO left in the text")
    for name in finding.figures:
        if not (figures_dir / name).exists():
            problems.append(f"figure file missing: {name}")
    return problems


print("report check:", check_report(finding.render_markdown(), R, tmp) or "no problems")
broken = finding.render_markdown().replace(f"{R['churn_after']:.1f}%", "5.1%") + "\nTODO: add chart"
print("on a damaged copy:", check_report(broken, R, tmp))
```
```text
report check: no problems
on a damaged copy: ['churn_after = 5.7% does not appear in the text', 'unfilled template placeholder or TODO left in the text']
```

### 7.5 Notebooks and scripts

Analysts often work in **Jupyter notebooks** (da.01) and then hand over a notebook. Three rules make a notebook a reproducible report rather than a scratchpad.

1. **Run top to bottom.** If a notebook only works when its cells are run in a special order, it is not a report. Before sharing: *Restart kernel and run all*.
2. **One parameters cell** at the top (the date, the file path, the periods), so a re-run changes inputs in one place.
3. **Move logic out of the notebook** into a module (`fb_metrics.py`) that has tests; the notebook imports it and tells the story. Cells that define the metrics are the first thing that goes stale.

A notebook is a JSON file. With `nbformat` we can build one from code, which is how a report generator emits a notebook for a colleague to continue from.

```python run
import nbformat
from nbformat import v4 as nbv4

nb = nbv4.new_notebook()
nb.cells = [
    nbv4.new_markdown_cell(f"# {finding.headline}\n\n*Rebuilt from code. Do not edit numbers by hand.*"),
    nbv4.new_code_cell("AS_OF = '2024-12-30'          # parameters: change here, then Restart and Run All\nDATA = 'data/panel.parquet'"),
    nbv4.new_code_cell("import pandas as pd\npanel = pd.read_parquet(DATA)\nassert panel['week'].max() <= pd.Timestamp(AS_OF)"),
    nbv4.new_markdown_cell("## Evidence\n" + "\n".join(f"- {e}" for e in finding.evidence)),
]
nbformat.validate(nb)
path = tmp / "report.ipynb"
nbformat.write(nb, path)
back = nbformat.read(path, as_version=4)
print("cells:", [c.cell_type for c in back.cells], "| valid notebook:", True, "| size:", path.stat().st_size, "bytes (machine-specific)")
```
```text
cells: ['markdown', 'code', 'code', 'markdown'] | valid notebook: True | size: 1562 bytes (machine-specific)
```

The notebook validates and has the structure of a good report: title, parameters, load-and-check, evidence. (Running it needs a Jupyter kernel; `jupyter nbconvert --execute` does it from the command line, and tools like papermill pass parameters.) For a recurring report, a plain script plus a scheduled job is simpler and more robust than a notebook; notebooks are best for exploration and for the final story.


## 8. Streamlit dashboards

### 8.1 What Streamlit is

A report is a snapshot. A **dashboard** lets the reader ask follow-up questions: "what about only the paid-ad customers?", "what about the 3-meal plan?". **Streamlit** turns a Python script into a web app with almost no web programming: you write Python that calls functions like `st.title`, `st.slider` and `st.line_chart`, and Streamlit shows them in a browser page.

The idea that makes it simple, and the one to remember: **the whole script runs again, from top to bottom, every time the reader touches a widget.** A widget (`st.slider`) is a function that returns its current value; when the reader moves the slider, the script reruns and the function returns the new value. There are no callbacks to wire up, no HTML, no state to manage in the simple case.

```text
reader moves a slider  ->  Streamlit reruns app.py from the top  ->  slider() returns the new value  ->  the page redraws
```

### 8.2 A first app, tested without a browser

An app is a `.py` file. To see it you run `streamlit run app.py` and open the address it prints. For tests, and for this chapter, we use Streamlit's **AppTest**, which runs the script in memory, lets us change widget values, and shows us the elements that the app produced. No browser opens, so the output is printable and checkable.

```python run
hello_code = '''
import streamlit as st

st.title("Churn calculator")
opening = st.slider("Opening customers", min_value=1000, max_value=10000, value=5000, step=500)
rate = st.slider("Monthly churn rate (%)", min_value=1.0, max_value=10.0, value=4.0, step=0.5)
lost = opening * rate / 100
st.metric("Customers lost per month", f"{lost:,.0f}")
st.write(f"At {rate:.1f}% churn, a base of {opening:,} loses about {lost:,.0f} customers a month.")
'''
hello_path = tmp / "hello_app.py"
hello_path.write_text(hello_code)

from streamlit.testing.v1 import AppTest

at = AppTest.from_file(str(hello_path), default_timeout=30).run()
print("exceptions:", len(at.exception))
print("title:", at.title[0].value)
print("sliders:", [(s.label, s.value) for s in at.slider])
print("metric:", at.metric[0].label, "=", at.metric[0].value)
```
```text
exceptions: 0
title: Churn calculator
sliders: [('Opening customers', 5000), ('Monthly churn rate (%)', 4.0)]
metric: Customers lost per month = 200
```

(Streamlit prints a harmless "missing ScriptRunContext" warning to the error stream when an app runs outside its server, as in tests; it is not part of the output below.) The app ran in memory with the default slider values: 5,000 customers at 4 percent lose 200 a month. Now the interaction: change a slider, rerun, and read the new result.

```python run
at.slider[1].set_value(6.0).run()
print("after setting churn to 6%:", at.metric[0].value)
print("text:", at.markdown[0].value)
at.slider[0].set_value(8000).run()
print("after setting the base to 8,000:", at.metric[0].value)
```
```text
after setting churn to 6%: 300
text: At 6.0% churn, a base of 5,000 loses about 300 customers a month.
after setting the base to 8,000: 480
```

Each `.run()` is one rerun of the whole script. The widget values are remembered by Streamlit between runs (in the **session state**), but nothing else is: any ordinary variable is created again at the top. That has two consequences. Slow work (loading a big file, fitting a model) must be **cached**, or the app will be slow on every click. And anything you want to remember beyond a widget value must be put in `st.session_state`.

### 8.3 The pieces you will use

| Piece | Functions | Notes |
|---|---|---|
| **Text** | `st.title`, `st.header`, `st.markdown`, `st.caption` | markdown for the findings page |
| **Inputs** | `st.slider`, `st.selectbox`, `st.multiselect`, `st.radio`, `st.checkbox`, `st.date_input`, `st.text_input`, `st.button` | each returns the current value |
| **Layout** | `st.sidebar`, `st.columns`, `st.tabs`, `st.expander`, `st.container` | filters in the sidebar, KPIs in columns |
| **Numbers** | `st.metric(label, value, delta=)` | a KPI tile with a change |
| **Tables** | `st.dataframe`, `st.table` | interactive or static |
| **Charts** | `st.line_chart`, `st.bar_chart`, `st.pyplot(fig)`, `st.plotly_chart(fig)`, `st.image` | native charts for quick views, matplotlib or plotly for control |
| **Control** | `st.stop()`, `st.warning`, `st.error`, `st.spinner` | handle empty or invalid input |
| **Performance** | `@st.cache_data`, `@st.cache_resource` | cache data and models |

### 8.4 Caching: not paying twice

`@st.cache_data` stores the result of a function keyed by its arguments. The second call with the same arguments returns the saved result instead of recomputing. We prove it with an app whose "expensive" function writes a line to a file each time it really runs.

```python run
log_path = tmp / "calls.log"
cache_code = f'''
import streamlit as st
from pathlib import Path

LOG = Path(r"{log_path}")

@st.cache_data
def expensive(n):
    with LOG.open("a") as f:
        f.write(f"computed {{n}}\\n")           # a line each time the function really runs
    return sum(i * i for i in range(n))

n = st.selectbox("n", [10, 100, 1000])
st.write(expensive(n))
'''
cache_path = tmp / "cache_app.py"
cache_path.write_text(cache_code)
log_path.write_text("")
c_at = AppTest.from_file(str(cache_path), default_timeout=30).run()
for choice in (100, 100, 1000, 10, 100, 1000):
    c_at.selectbox[0].select(choice).run()
print("reruns:", 7, "| value shown last:", c_at.markdown[0].value)
print("times the function really ran:", len(log_path.read_text().splitlines()), "->", log_path.read_text().split())
```
```text
reruns: 7 | value shown last: `332833500`
times the function really ran: 3 -> ['computed', '10', 'computed', '100', 'computed', '1000']
```

Seven reruns (the first plus six selections), but only **three** real computations: one for each distinct value of `n` (10, 100 and 1000), because the cache returns the saved result for repeats. Two warnings: the cache key is the function's arguments, so everything the result depends on must be an argument; and cached data are shared by all users of the app, so never cache something personal.

### 8.5 Designing a dashboard

A dashboard is not a report with buttons. Five rules.

1. **The default view tells the story.** A manager who opens the page and clicks nothing should already see the headline and the KPIs.
2. **KPIs first, details below.** A row of `st.metric` tiles at the top (value, and the change against a baseline), then charts, then tables.
3. **Few filters, with good defaults.** Every filter doubles the number of states to test. Offer the ones that match real questions (channel, plan, city) and start with everything selected.
4. **State the definitions on the page.** A churn tile without "of opening actives, last active week in the month" is a rumour (da.06).
5. **Handle empty and extreme states.** If the reader deselects every channel, show a message, not a crash.

And one rule about *code*: **the dashboard only displays; the logic lives in a module with tests.** If the numbers are computed inside `app.py`, the dashboard and the written report will eventually disagree. We now build that structure.

## 9. Project: a dashboard with a findings page

**The brief.** The head of operations wants the churn analysis available to the whole team as an interactive page. It must have: a **Findings** tab with the written one-pager of section 6; an **Explore** tab where anyone can filter by channel, plan and city and see the KPIs, the monthly churn, and the effect of late boxes; and a **Data notes** tab with definitions, provenance and caveats. It must be tested.

### 9.1 The structure

```text
dashboard/
  app.py            the Streamlit page (display only)
  fb_metrics.py     the logic: loading, filtering, KPIs (tested)
  findings.md       the written finding (generated by code)
  overview.png, contributions.png     figures used by the findings page
  data/customers.parquet, data/panel.parquet
```

### 9.2 The logic module

The functions of this chapter move into a module, so that the report and the dashboard use **the same code**. We write it and then test that it reproduces the numbers we computed in sections 3 to 6.

```python run
dash = tmp / "dashboard"
(dash / "data").mkdir(parents=True)

module_code = '''
"""FreshBox churn metrics. The dashboard displays these numbers; it does not compute them."""
import pandas as pd


def load(folder):
    customers = pd.read_parquet(folder / "customers.parquet")
    panel = pd.read_parquet(folder / "panel.parquet")
    return customers, panel


def filter_data(customers, panel, channels, plans, cities):
    """Customers and panel rows for the chosen segments, or None if the selection is empty."""
    if not channels or not plans or not cities:
        return None
    cus = customers[customers["channel"].isin(channels) & customers["plan"].isin(plans) & customers["city"].isin(cities)]
    pan = panel[panel["customer_id"].isin(cus["customer_id"])]
    return (cus, pan) if len(pan) else None


def monthly_kpis(customers, panel):
    """One row per month: opening actives, churned, churn rate, on-time rate, weekly revenue (see the KPI definitions)."""
    p = panel.assign(month=panel["week"].dt.to_period("M"))
    first = p.groupby("month")["week"].min()
    opening = p[p["week"].isin(first.values)][["customer_id", "month"]]
    opening = opening.merge(customers[["customer_id", "last_week"]], on="customer_id", how="left", validate="m:1")
    opening["churned"] = opening["last_week"].dt.to_period("M") == opening["month"]
    out = opening.groupby("month").agg(opening_actives=("customer_id", "size"), churned=("churned", "sum"))
    out["churn_rate_pct"] = out["churned"] / out["opening_actives"] * 100
    out["on_time_pct"] = (1 - p.groupby("month")["late"].mean()) * 100
    out["weekly_revenue_k"] = p.groupby(["month", "week"])["price"].sum().groupby("month").mean() / 1000
    return out


def baseline(kpis, start="2024-04", end="2024-08"):
    """The reference period for comparisons: the average churn and on-time rate before the problem."""
    b = kpis.loc[start:end]
    return {"churn": float(b["churn_rate_pct"].mean()), "on_time": float(b["on_time_pct"].mean())}


def late_effect_table(customers, panel):
    """Weekly churn per 1,000 customer-weeks with and without a late box in the last 3 weeks."""
    pn = panel.merge(customers[["customer_id", "last_week"]], on="customer_id", how="left", validate="m:1")
    pn = pn.sort_values(["customer_id", "week"])
    pn["churn_now"] = pn["week"] == pn["last_week"]
    pn["late_in_3"] = pn.groupby("customer_id")["late"].rolling(3, min_periods=1).sum().reset_index(level=0, drop=True).to_numpy()
    pn["late_recent"] = pn["late_in_3"] > 0
    g = pn.groupby("late_recent")["churn_now"].agg(churn_events="sum", customer_weeks="size")
    g["churn_per_1000"] = g["churn_events"] / g["customer_weeks"] * 1000
    g.index = g.index.map({False: "no late box", True: "late box in last 3 weeks"})
    return g
'''
(dash / "fb_metrics.py").write_text(module_code)

customers.to_parquet(dash / "data" / "customers.parquet")
panel.to_parquet(dash / "data" / "panel.parquet")
sys.path.insert(0, str(dash))
import importlib
import fb_metrics as fm
importlib.reload(fm)

c2, p2 = fm.load(dash / "data")
print("loaded:", c2.shape, p2.shape)
pd.testing.assert_frame_equal(fm.monthly_kpis(c2, p2), kpi)
print("module KPIs equal the KPIs of section 3: True")
b = fm.baseline(kpi)
print("baseline:", {k: round(v, 2) for k, v in b.items()}, "| equals section 3's Apr-Aug figures:", abs(b["churn"] - R["churn_before"]) < 1e-9 or abs(b["churn"] - float(kpi.loc["2024-04":"2024-08", "churn_rate_pct"].mean())) < 1e-9)
tbl = fm.late_effect_table(c2, p2)
print(tbl.round(2).to_string())
print("filter with an empty channel list returns:", fm.filter_data(c2, p2, [], ["2-meal"], ["Metro"]))
```
```text
loaded: (8000, 6) (337776, 5)
module KPIs equal the KPIs of section 3: True
baseline: {'churn': 4.06, 'on_time': 91.98} | equals section 3's Apr-Aug figures: True
                          churn_events  customer_weeks  churn_per_1000
late_recent                                                           
no late box                       1905          243463            7.82
late box in last 3 weeks          1997           94313           21.17
filter with an empty channel list returns: None
```

The module's KPI table is identical to the one computed in section 3 (the assertion would have failed otherwise). This is the **reconciliation** of da.06 applied to our own work: the dashboard and the report give the same numbers because they are the same code. Now a unit test of the logic itself, on a tiny table whose answer we can compute by hand:

```python run
def test_monthly_kpis_on_tiny_data():
    cus = pd.DataFrame({"customer_id": [1, 2, 3], "last_week": pd.to_datetime(["2024-01-15", pd.NaT, "2024-02-05"])})
    pan = pd.DataFrame({
        "customer_id": [1, 1, 2, 2, 2, 3, 3],
        "week": pd.to_datetime(["2024-01-01", "2024-01-08", "2024-01-01", "2024-01-08", "2024-02-05", "2024-01-01", "2024-01-08"]),
        "late": [False, True, False, False, False, False, False], "price": [100, 100, 100, 100, 100, 100, 100], "tenure_wk": 0})
    k = fm.monthly_kpis(cus, pan)
    jan = k.loc[pd.Period("2024-01")]
    assert jan["opening_actives"] == 3, f"3 customers had a box in the first week of January, got {jan['opening_actives']}"
    assert jan["churned"] == 1, f"only customer 1 has its last active week in January (customer 3 leaves in February), got {jan['churned']}"
    assert abs(jan["churn_rate_pct"] - 100 / 3) < 1e-9, "the churn rate should be 1 of 3 = 33.3%"
    assert abs(jan["on_time_pct"] - (1 - 1 / 6) * 100) < 1e-9, "1 late box in 6 January boxes means 83.3% on time"


test_monthly_kpis_on_tiny_data()
print("test_monthly_kpis_on_tiny_data passed")
```
```text
test_monthly_kpis_on_tiny_data passed
```

By hand: in January three customers had a box in the first week; only customer 1 ended its subscription in January (customer 3's last week is in February). So 1 of 3 churned. There are 6 January boxes (customers 1 and 3 have two each, customer 2 has two), one late: 83.3 percent on time. The test pins the definitions down, with a message for each likely mistake.

### 9.3 The findings page and the app

The findings page is generated from the finding (section 6); the app displays it.

```python run
(dash / "findings.md").write_text(finding.render_markdown())
for name in ("overview.png", "contributions.png"):
    (dash / name).write_bytes((tmp / name).read_bytes())

app_code = '''
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import fb_metrics as fm

st.set_page_config(page_title="FreshBox churn", layout="wide")


@st.cache_data
def get_data():
    return fm.load(HERE / "data")


@st.cache_data
def explore(channels, plans, cities):
    """KPIs and the late-box table for a selection (arguments are tuples, so they can be cached)."""
    customers, panel = get_data()
    sel = fm.filter_data(customers, panel, list(channels), list(plans), list(cities))
    if sel is None:
        return None
    cus, pan = sel
    return fm.monthly_kpis(cus, pan), fm.late_effect_table(cus, pan)


customers, panel = get_data()
st.title("FreshBox: why did churn rise?")
st.caption(f"Synthetic data, weeks from {panel['week'].min():%d %b %Y} to {panel['week'].max():%d %b %Y}. "
           "Monthly churn = share of the customers active in the first week of the month whose last active week falls in the month.")

with st.sidebar:
    st.header("Filters")
    all_channels, all_plans, all_cities = (sorted(customers[c].unique()) for c in ("channel", "plan", "city"))
    channels = st.multiselect("Channel", all_channels, default=all_channels)
    plans = st.multiselect("Plan", all_plans, default=all_plans)
    cities = st.multiselect("City", all_cities, default=all_cities)

tab_find, tab_explore, tab_notes = st.tabs(["Findings", "Explore", "Data notes"])

with tab_find:
    st.markdown((HERE / "findings.md").read_text())
    st.image(str(HERE / "overview.png"), caption="Monthly churn and the share of boxes delivered on time.")
    st.image(str(HERE / "contributions.png"), caption="Contribution of each cause to the rise in churn.")

with tab_explore:
    result = explore(tuple(channels), tuple(plans), tuple(cities))
    if result is None:
        st.warning("Select at least one value in every filter.")
        st.stop()
    kpis, late = result
    ref = fm.baseline(kpis)
    last = kpis.index[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Opening actives, {last}", f"{int(kpis['opening_actives'].iloc[-1]):,}")
    c2.metric(f"Monthly churn, {last}", f"{kpis['churn_rate_pct'].iloc[-1]:.1f}%",
              delta=f"{kpis['churn_rate_pct'].iloc[-1] - ref['churn']:+.1f} points vs Apr-Aug 2024", delta_color="inverse")
    c3.metric(f"Boxes on time, {last}", f"{kpis['on_time_pct'].iloc[-1]:.0f}%",
              delta=f"{kpis['on_time_pct'].iloc[-1] - ref['on_time']:+.0f} points vs Apr-Aug 2024")
    st.subheader("Monthly churn rate (%)")
    chart = kpis[["churn_rate_pct"]].copy()
    chart.index = chart.index.to_timestamp()
    st.line_chart(chart)
    st.subheader("Weekly churn per 1,000 customer-weeks, by recent late delivery")
    st.dataframe(late.round(2))
    st.bar_chart(late["churn_per_1000"])

with tab_notes:
    st.markdown("""
**Definitions.** *Opening actives*: customers who received a box in the first week of the month. *Monthly churn*: the share of them whose last
active week falls in the month. *On time*: share of boxes delivered on time. *Late box in last 3 weeks*: a late box in this or the two previous weeks.

**Caveats.** The data are synthetic. The effect of late deliveries is observational (see the Findings tab for the confidence statement).
Churn for small selections is noisy: check the number of opening actives before reading a rate.
""")
'''
(dash / "app.py").write_text(app_code)
print(sorted(p.name for p in dash.iterdir() if not p.name.startswith("__")))
print("app.py lines:", len(app_code.strip().splitlines()), "| fb_metrics.py lines:", len(module_code.strip().splitlines()))
```
```text
['app.py', 'contributions.png', 'data', 'fb_metrics.py', 'findings.md', 'overview.png']
app.py lines: 78 | fb_metrics.py lines: 50
```

The app is about 80 lines, and none of them computes a KPI: it loads, filters through the module, and displays. Notice the design: the sidebar filters feed one cached function, `explore`, whose arguments are tuples (hashable, so cacheable); the empty selection returns `None` and the page shows a warning and stops; the churn tile shows the change against a **named baseline** ("vs Apr-Aug 2024") with the delta coloured as bad when it rises (`delta_color="inverse"`).

### 9.4 Test the dashboard

```python run
app = AppTest.from_file(str(dash / "app.py"), default_timeout=120)
app.run()
print("exceptions:", len(app.exception))
print("title:", app.title[0].value)
print("tabs:", [t.label for t in app.tabs])
print("sidebar filters:", [(m.label, len(m.value)) for m in app.sidebar.multiselect])
for m in app.metric:
    print(f"  metric: {m.label:30} {m.value:>8}   {m.delta}")
```
```text
exceptions: 0
title: FreshBox: why did churn rise?
tabs: ['Findings', 'Explore', 'Data notes']
sidebar filters: [('Channel', 3), ('Plan', 2), ('City', 3)]
  metric: Opening actives, 2024-12          4,381   
  metric: Monthly churn, 2024-12             6.5%   +2.4 points vs Apr-Aug 2024
  metric: Boxes on time, 2024-12              79%   -13 points vs Apr-Aug 2024
```

The default view shows the three filters with everything selected, and the three KPI tiles for the latest month: churn of about 6.5 percent against a baseline of 4.1, and an on-time rate of 79 percent. Now check the values against the module (and so against section 3), then change the filters.

```python run
k_all = fm.monthly_kpis(c2, p2)
churn_tile = [m for m in app.metric if m.label.startswith("Monthly churn")][0]
assert churn_tile.value == f"{k_all['churn_rate_pct'].iloc[-1]:.1f}%", "the churn tile must equal the KPI computed by the module"
print("churn tile equals the module's KPI:", churn_tile.value)

app.sidebar.multiselect[0].set_value(["paid"]).run()
sel = fm.filter_data(c2, p2, ["paid"], list(sorted(c2["plan"].unique())), list(sorted(c2["city"].unique())))
k_paid = fm.monthly_kpis(*sel)
tile = [m for m in app.metric if m.label.startswith("Monthly churn")][0]
print("paid customers only: churn tile", tile.value, "| module:", f"{k_paid['churn_rate_pct'].iloc[-1]:.1f}%", "| opening actives tile:", app.metric[0].value)
assert tile.value == f"{k_paid['churn_rate_pct'].iloc[-1]:.1f}%"
assert not app.exception

app.sidebar.multiselect[0].set_value([]).run()
print("empty channel selection -> warning:", [w.value for w in app.warning], "| exceptions:", len(app.exception))
```
```text
churn tile equals the module's KPI: 6.5%
paid customers only: churn tile 8.6% | module: 8.6% | opening actives tile: 1,373
empty channel selection -> warning: ['Select at least one value in every filter.'] | exceptions: 0
```

Filtering to paid customers raises the churn tile (paid customers churn more, as we found in 4.4), and the tile equals the module's value for the same selection. With **no** channel selected the page shows the warning instead of failing. A last test goes through a grid of filter combinations and checks that none raises an exception: a **smoke test**.

```python run
import itertools, time
t0 = time.perf_counter()
channels_all = ["organic", "paid", "referral"]
plans_all = ["2-meal", "3-meal"]
cities_all = ["Large", "Metro", "Small"]
combos = [(["paid"], plans_all, cities_all), (channels_all, ["3-meal"], cities_all), (channels_all, plans_all, ["Small"]),
          (["referral"], ["2-meal"], ["Metro"]), ([], plans_all, cities_all), (channels_all, [], cities_all)]
rows = []
for ch, pl, ci in combos:
    a = AppTest.from_file(str(dash / "app.py"), default_timeout=120).run()
    a.sidebar.multiselect[0].set_value(ch)
    a.sidebar.multiselect[1].set_value(pl)
    a.sidebar.multiselect[2].set_value(ci)
    a.run()
    tile = [m.value for m in a.metric if m.label.startswith("Monthly churn")]
    rows.append({"channel": ",".join(ch) or "-", "plan": ",".join(pl) or "-", "city": ",".join(ci) or "-",
                 "exceptions": len(a.exception), "warning": bool(a.warning), "churn tile": tile[0] if tile else "(none)"})
print(pd.DataFrame(rows).to_string(index=False))
print("smoke test: no exceptions in any combination:", all(r["exceptions"] == 0 for r in rows), f"| took {time.perf_counter() - t0:.0f} s (machine-specific)")
```
```text
              channel          plan              city  exceptions  warning churn tile
                 paid 2-meal,3-meal Large,Metro,Small           0    False       8.6%
organic,paid,referral        3-meal Large,Metro,Small           0    False       7.0%
organic,paid,referral 2-meal,3-meal             Small           0    False       6.0%
             referral        2-meal             Metro           0    False       3.8%
                    - 2-meal,3-meal Large,Metro,Small           0     True     (none)
organic,paid,referral             - Large,Metro,Small           0     True     (none)
smoke test: no exceptions in any combination: True | took 3 s (machine-specific)
```

Six combinations, no exceptions; the two empty selections show the warning and no churn tile; the others show a plausible churn rate (referral customers in Metro on the 2-meal plan have a small base, and a noisy number: the Data notes tab warns about it). This is the test suite of a dashboard: the values against the module, the interactions, the empty states, and a smoke test over a grid.

### 9.5 Run it yourself

```text
cd dashboard
streamlit run app.py          # opens http://localhost:8501
```

Change a filter and watch the tiles and the charts change. Open the Findings tab: it is the page a manager reads first. To share the dashboard, a team can host it on an internal server, or on Streamlit's community hosting (that needs the internet, which this module does not assume). When you hand it over, hand over the **tests** too.

### 9.6 What to hand in, for an analysis of your own

1. A **precise question** and the decision behind it, in two sentences.
2. A **KPI table** with definitions (numerator, denominator, date basis, owner, target, guardrail).
3. A **hypothesis table** written before testing: prediction and refutation for each.
4. An **evidence table** with test, result with its uncertainty, and a verdict; and a **log** of what you tried.
5. A **one-page finding** in the template of 1.4, generated from a dictionary of computed numbers, passing the finding linter.
6. A **logic module** with unit tests on a tiny table, and the dashboard (display only) with AppTest tests: defaults, values against the module, interactions, empty state, smoke test.
7. A **provenance footer**: data fingerprint, row counts, date range, analysis date.
8. A **limitations paragraph** that you would be comfortable defending.

## 10. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Starting with charts, not a question | forty plots and no answer | write the question and the decision first (1.1, 4.1) |
| Hypotheses written after seeing the data | any pattern "confirms" a story | write predictions and refutations first; keep a log (4.1) |
| Many comparisons, report the winner | false discoveries | decide the comparisons beforehand; correct (da.08) |
| Comparing unlike periods | a young base looks like high churn | compare like with like; use tenure and a decomposition (4.2, 4.5) |
| Mix against rate confusion | a change explained by who is in the base, or the reverse | the mix and rate decomposition (4.5) |
| Missing value meaning "still active" dropped | survivors removed | ask why a value is missing (2.2) |
| Correlation in time as cause | two things moved in September | comparison groups, dose, the model, the counterfactual (5) |
| Reporting a model without a sanity check | a clever number nobody trusts | a simple second method must agree (7.2) |
| One estimate, no interval | false precision | every number with its interval (6.1) |
| Hiding the weak hypothesis | a later surprise | report secondary and inconclusive results with their size (5.4, 6.3) |
| Recommendations without owner or date | nothing happens | action, owner, date, success measure (6.1) |
| A point impact | a promise you cannot keep | a range, with the cost beside it (6.2) |
| Numbers typed by hand | the text goes stale | generate the text from the numbers (6.2, 7.4) |
| Findings with vague phrases | the reader cannot act | the finding linter (6.4) |
| Starting with the story of your analysis | the answer is buried | the pyramid: answer first (1.3) |
| Logic inside the dashboard | the dashboard and the report disagree | a tested module; the app only displays (9.2) |
| No caching | every click reloads the data | `@st.cache_data` with hashable arguments (8.4) |
| Untested filters | a crash on an empty selection | AppTest: defaults, values, empty state, smoke test (9.4) |
| Dashboard without definitions | tiles that mean different things to different people | put definitions and caveats on the page (8.5) |
| No provenance | "which data was this?" | fingerprint, row counts, dates in every report (7.3) |

A habit for every finding you send: read the first two lines as if they were the only thing the reader sees. If they do not contain the answer and the action, rewrite them.

## 11. Summary

- The analyst's job is a **decision**. The flow is: **question, analysis, finding, recommendation, limitations**. A finding is actionable when it has a claim with a number, a size with its uncertainty, an action with an owner and a date, an impact range, the main limits, and a success measure. Write **answer first** (the pyramid), not in the order you discovered it.
- **KPIs** are metrics you steer by: tied to a decision, precisely defined (da.06), owned, comparable, normalised, timely and hard to game. Separate **leading** from **lagging** indicators, avoid **vanity** metrics, add **guardrails**, remember **Goodhart's law**, and draw the **KPI tree** to see where a change can come from.
- **Hypothesis-driven EDA**: turn a worry into a precise question, list explanations from the KPI tree, write for each what you should see and what would refute it, then test with the smallest analysis that can refute it. Keep a log. Look at the time profile, cut by segment, and use the **mix against rate decomposition** to tell "who is in the base" from "how each group behaves".
- **Testing hypotheses** combines tools from the whole module: rate ratios with intervals, a **dose-response** check (and report honestly when it is absent), balance checks on the cause, a **hazard model** with cluster-robust errors, a **difference in differences** with a comparison group, a **comparison with last year** for season, and **counterfactuals** that attribute the change to each cause with parametric-bootstrap intervals. An **evidence table** gives each hypothesis a verdict: supported, secondary, inconclusive, rejected.
- **Writing the finding**: a template (headline, recommendation, impact, evidence, confidence, limitations, next steps); numbers computed once in a dictionary and rendered into the text; a **finding linter** that catches missing numbers, owners, dates, ranges, uncertainty and vague phrases; two or three figures checked as in da.09; versions for different readers generated from the same numbers.
- **Reports as code**: stages (load, check, compute, write, check), parameters like the **as-of date** (complete months only), a **quick method** that agrees with the full model, **provenance** (data fingerprint, rows, dates), tests on the report, and notebooks that run top to bottom with one parameters cell and logic in a tested module.
- **Streamlit** reruns the script on every interaction: widgets return values; `st.sidebar`, `st.columns`, `st.tabs` and `st.metric` organise the page; `@st.cache_data` avoids recomputing; the dashboard **only displays**, the logic lives in a tested module. **AppTest** runs the app headlessly so you can test defaults, values against the module, interactions, empty states and a smoke grid.

You reached the outcome of this chapter: you can **write a one-page finding that a manager can act on**. The FreshBox analysis started with "churn jumped, what happened?" and ended with a page that says what changed (4.0 to 5.7 percent), why (late deliveries, about 1.4 of the 1.4 modelled points, with an interval), what to do (owners and dates), what it is worth (about 65 customers and 48,000 rupees of weekly revenue a month, as a range), how sure we are, and how we will know it worked; and a dashboard that lets the team explore it, with tests. Next, da.11 applies the same discipline to the standard business analyses of the role: A/B tests, funnel, cohort and retention analysis, and RFM customer segmentation, ending in a full customer analysis with recommendations and limitations.
