# Chapter 11 (DA): Applied business analytics

The ten chapters before this one gave you the pieces: clean data, precise metrics, SQL, statistics, charts, and the discipline to turn findings into decisions. This chapter applies them to the three analyses that every customer-facing business runs again and again. **A/B testing** answers "did this change work?". **Funnel, cohort and retention analysis** answers "where do customers drop out, and do the ones we win stay?". **RFM segmentation** answers "who are our customers, and what should we do differently for each group?". Together they make up the core of what an analyst in a shop, an app or a subscription business is asked to do.

By the end of this chapter you reach one outcome: **you can run a full customer analysis and present recommendations with their limitations**. That means: design and read an experiment correctly, find the leaks in a funnel and size them, build a cohort retention table and a customer-value estimate, segment customers by behaviour and check that the segments mean something, and then bring it all into one recommendation with ranges, confidence and the things you do not know.

Prerequisites: da.10 (the analyst's workflow, hypothesis-driven EDA, the finding template and the linter), da.08 (intervals, p-values, power, confounding) and da.07 (cohort and funnel logic in SQL). Here the same ideas appear in pandas and with the business reading attached; da.07's warnings about immature cohorts and denominators apply in full.

> **Offline rule for this chapter.** pandas, NumPy, SciPy, statsmodels and scikit-learn are installed in the course environment. No internet is needed. Every dataset is **synthetic**, built in code with seeded random numbers, so you get the same numbers I did. The shop, its customers and its experiment are invented. Because we built the world, we know the **true** effects (the real lift of the experiment, the real differences between channels), so you can see whether each method finds them. Every output block below was produced by running the code above it, in one session from top to bottom. **Versions are machine-specific.** Some blocks run thousands of simulated experiments; they finish in seconds.

```python run
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels
import sklearn
from scipy import stats
import statsmodels.api as sm

print("python      ", sys.version.split()[0])
print("pandas      ", pd.__version__)
print("numpy       ", np.__version__)
print("scipy       ", scipy.__version__)
print("statsmodels ", statsmodels.__version__)
print("scikit-learn", sklearn.__version__)
```
```text
python       3.14.4
pandas       3.1.1
numpy        2.5.4
scipy        1.18.1
statsmodels  0.15.0
scikit-learn 1.9.1
```

Two setup lines make the printed tables compact.

```python run
pd.set_option("display.width", 115)
pd.set_option("display.max_columns", 14)
pd.set_option("display.max_rows", 30)
pd.set_option("display.float_format", "{:,.2f}".format)
print("display options set")
```
```text
display options set
```

## Table of contents

1. [The case: ShopNest](#1-the-case-shopnest)
2. [A/B testing](#2-ab-testing)
3. [Funnel analysis](#3-funnel-analysis)
4. [Cohorts, retention and customer value](#4-cohorts-retention-and-customer-value)
5. [RFM segmentation](#5-rfm-segmentation)
6. [From analyses to a recommendation](#6-from-analyses-to-a-recommendation)
7. [Project: a customer analytics case study](#7-project-a-customer-analytics-case-study)
8. [Common traps](#8-common-traps)
9. [Summary](#9-summary)

## 1. The case: ShopNest

### 1.1 The business and its four questions

**ShopNest** is a synthetic online shop for home goods. It has 6,000 customers acquired from four channels (organic search, paid ads, email and referral) between January 2023 and mid-December 2024, and the data end on 31 December 2024. The head of growth brings four questions, which map to the four methods of this chapter:

| # | Question from the business | Method | Section |
|---|---|---|---|
| Q1 | "We tested a free-shipping banner on the cart page. Should we roll it out?" | A/B test | 2 |
| Q2 | "Where do shoppers drop out between visit and purchase, and which leak is worth fixing first?" | funnel analysis | 3 |
| Q3 | "Do customers from each channel come back, and what is a customer worth?" | cohorts, retention, LTV | 4 |
| Q4 | "Who are our best customers, who is slipping away, and what should marketing do for each group?" | RFM segmentation | 5 |

Section 6 turns the four answers into one set of recommendations, with ranges and limits.

### 1.2 The tables

```python run
CUT = pd.Timestamp("2024-12-31")                          # the last day of data


def make_shop(seed=31, n=6000):
    rng = np.random.default_rng(seed)
    days = (pd.Timestamp("2024-12-15") - pd.Timestamp("2023-01-01")).days + 1
    first = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, days, n), unit="D")          # date of the first order
    channel = rng.choice(["organic", "paid", "email", "referral"], n, p=[.40, .35, .15, .10])
    city = rng.choice(["Metro", "Large", "Small"], n, p=[.45, .35, .20])
    lam_base = pd.Series(channel).map({"organic": .35, "paid": .22, "email": .45, "referral": .50}).to_numpy()   # TRUTH: orders per month early on
    tau = pd.Series(channel).map({"organic": 10, "paid": 6, "email": 12, "referral": 14}).to_numpy()            # TRUTH: months over which interest fades
    lam = lam_base * rng.gamma(2, .5, n)                                      # customers differ a lot in how often they buy
    avg = np.exp(rng.normal(6.6, .35, n))                                     # each customer's typical basket (rupees)
    rows = []
    for i in range(n):
        months = (CUT - first[i]).days / 30.44
        rows.append((i, first[i], avg[i] * rng.lognormal(0, .3)))               # the first order is the acquisition event
        t = 0.0
        while t < months:                                                       # repeat orders: a fading Poisson process, month by month
            step = min(1.0, months - t)
            for _ in range(rng.poisson(lam[i] * np.exp(-t / tau[i]) * step)):
                d = first[i] + pd.Timedelta(days=float((t + rng.random() * step) * 30.44))
                if d <= CUT:
                    rows.append((i, d, avg[i] * rng.lognormal(0, .3)))
            t += step
    orders = pd.DataFrame(rows, columns=["customer_id", "order_date", "amount"])
    orders["amount"] = orders["amount"].round(0)
    orders["order_date"] = orders["order_date"].dt.normalize()
    customers = pd.DataFrame({"customer_id": np.arange(n), "first_order": first.normalize(), "channel": channel, "city": city})
    return customers, orders


customers, orders = make_shop()
print("customers", customers.shape, "| grain: one row per customer")
print("orders   ", orders.shape, "| grain: one row per order")
print(orders.head(3).to_string(index=False))
```
```text
customers (6000, 4) | grain: one row per customer
orders    (18740, 3) | grain: one row per order
 customer_id order_date  amount
           0 2024-01-28  368.00
           0 2024-05-11  706.00
           1 2024-10-07  632.00
```

The audit habit of da.10: grain, keys, coverage, plausibility.

```python run
print("customer_id unique:", customers["customer_id"].is_unique, "| every order has a known customer:", bool(orders["customer_id"].isin(customers["customer_id"]).all()))
print("orders per customer: min", orders.groupby("customer_id").size().min(), "| median", int(orders.groupby("customer_id").size().median()), "| max", orders.groupby("customer_id").size().max())
print("date range of orders:", orders["order_date"].min().date(), "to", orders["order_date"].max().date())
first_check = orders.groupby("customer_id")["order_date"].min()
print("first order date in `customers` matches the first order in `orders`:", bool((first_check.reindex(customers["customer_id"]).to_numpy() == customers["first_order"].to_numpy()).all()))
print("total revenue:", f"{orders['amount'].sum():,.0f}", "| orders:", len(orders), "| average order value:", f"{orders['amount'].mean():,.0f}")
```
```text
customer_id unique: True | every order has a known customer: True
orders per customer: min 1 | median 2 | max 25
date range of orders: 2023-01-01 to 2024-12-30
first order date in `customers` matches the first order in `orders`: True
total revenue: 15,418,418 | orders: 18740 | average order value: 823
```

Two tables carry the whole story of sections 4 and 5. The experiment of section 2 and the sessions of section 3 are separate tables, introduced where they are used.

## 2. A/B testing

### 2.1 What an experiment is, and why it beats everything else

In da.08 you saw that observational comparisons are confounded: customers who choose a feature differ from those who do not. A **randomised controlled experiment**, called an **A/B test** in business, removes the problem by design. You split the visitors at random into a **control** group (A, the current experience) and a **treatment** group (B, the change). Because the assignment is a coin flip, the two groups are alike in everything, measured or not, apart from the change. Any later difference in outcome is due to the change (plus luck, which statistics measures).

The recipe has six steps, and most of the mistakes are made in the first three, before any data exist.

| Step | Question | Our test |
|---|---|---|
| 1. **Hypothesis** | what change, what effect, why? | a free-shipping banner on the cart page raises the share of visitors who buy |
| 2. **Metrics** | one **primary** metric; **guardrails** that must not get worse | primary: conversion rate. Guardrails: average order value, revenue per visitor |
| 3. **Design** | unit of randomisation, size, duration | the visitor; sample size from a power calculation; whole weeks |
| 4. **Run** | randomise, do not touch, do not peek | 14 days, 50/50 split |
| 5. **Check** | did the randomisation work? | sample ratio check |
| 6. **Analyse and decide** | effect with its interval, against the minimum effect that matters | the decision rule of da.08 |

### 2.2 Step 2 to 3: how many visitors do we need?

Before the test, decide the **minimum effect worth detecting** (the *minimum detectable effect*, MDE) and how sure you want to be. The business says: shipping subsidies cost money, so the banner only pays if conversion rises by at least **0.5 percentage points** (from the current 6 percent). Two error rates matter: **alpha**, the chance of a false alarm when there is no effect (0.05), and **power**, the chance of detecting an effect of the MDE size when it is real (we want 0.80). For two proportions the sample size per group is

```text
n per group = 2 x (z_alpha/2 + z_power)^2 x p x (1 - p) / (difference)^2
```

with `z_alpha/2 = 1.96` and `z_power = 0.84` for 5 percent and 80 percent. The formula shows the three forces: a smaller effect needs far more visitors (quadratically), a noisier metric needs more, and more power needs more.

```python run
def n_per_group(p0, mde, alpha=0.05, power=0.80):
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    p1 = p0 + mde
    p_bar = (p0 + p1) / 2
    return int(np.ceil(2 * (z_a + z_b) ** 2 * p_bar * (1 - p_bar) / mde ** 2))


for mde in (0.010, 0.007, 0.005, 0.003):
    print(f"detect +{mde * 100:.1f} points from 6.0%: {n_per_group(0.06, mde):7,} visitors per group")
print()
print("with statsmodels:", int(np.ceil(sm.stats.NormalIndPower().solve_power(
    effect_size=sm.stats.proportion_effectsize(0.065, 0.06), alpha=0.05, power=0.8, ratio=1))), "per group for +0.5 points")
```
```text
detect +1.0 points from 6.0%:   9,541 visitors per group
detect +0.7 points from 6.0%:  19,052 visitors per group
detect +0.5 points from 6.0%:  36,792 visitors per group
detect +0.3 points from 6.0%: 100,672 visitors per group

with statsmodels: 36778 per group for +0.5 points
```

To detect +0.5 points we need about **37,000 visitors per group**; shrinking the effect to +0.3 points would need nearly three times as many (about 100,000). This is the first practical lesson: *decide the smallest effect that matters before you run the test*, because it fixes the cost. (The tiny gap between our formula and statsmodels is the choice of the pooled variance; both are standard.) The shop has about 1,700 visitors a day who reach the cart page, so a 50/50 split needs about 43 days to reach 37,000 per group. The business could not wait that long, and the test ran for 14 days with 12,000 visitors in each group. That is **an underpowered test** for the effect that matters, and we handle it honestly below.

```python run
def power_for(p0, mde, n, alpha=0.05):
    p1 = p0 + mde
    se = np.sqrt(p0 * (1 - p0) / n + p1 * (1 - p1) / n)
    return float(1 - stats.norm.cdf(stats.norm.ppf(1 - alpha / 2) - mde / se))


for n in (6000, 12000, 18000, 24000):
    print(f"{n:6,} per group: power to detect +0.5 points = {power_for(0.06, 0.005, n) * 100:4.0f}%   | to detect +0.7 points = {power_for(0.06, 0.007, n) * 100:4.0f}%")
```
```text
 6,000 per group: power to detect +0.5 points =   20%   | to detect +0.7 points =   35%
12,000 per group: power to detect +0.5 points =   36%   | to detect +0.7 points =   60%
18,000 per group: power to detect +0.5 points =   50%   | to detect +0.7 points =   78%
24,000 per group: power to detect +0.5 points =   62%   | to detect +0.7 points =   88%
```

With 12,000 per group the test has about a 36 percent chance of detecting a true +0.5-point lift, and about 60 percent for +0.7. Running an underpowered test is not forbidden, but you must say so before the result, and you must not read "not significant" as "no effect" (da.08).

> **Predict the output.** Suppose the shop's baseline conversion were 3 percent instead of 6, and we still wanted to detect an absolute lift of +0.5 points. Would we need more or fewer visitors per group?

<details><summary>Answer</summary>

```python run
print("baseline 6%:", f"{n_per_group(0.06, 0.005):,}", "per group")
print("baseline 3%:", f"{n_per_group(0.03, 0.005):,}", "per group")
```
```text
baseline 6%: 36,792 per group
baseline 3%: 19,744 per group
```

Fewer: about 20,000 against 37,000. The formula contains `p(1 - p)`, the variance of a yes/no outcome, which is smaller for a rarer event, so the same *absolute* lift is easier to detect against a 3 percent baseline. (A lift of +0.5 points is, however, a much larger *relative* lift on 3 percent, 17 percent against 8 percent, which is also why relative lifts alone say little about how hard a test will be.)

</details>

### 2.3 The experiment data

Our test ran for 14 days with 12,000 visitors in each group. The factory also builds a *pre-experiment* column, the visitor's number of orders in the previous 90 days, which we use later to sharpen the analysis. We know the truth, which the analyst would not: the banner raises the odds of buying by about 12 percent (about +0.7 points) and lowers the average basket a little (3 percent: free shipping lets people buy smaller baskets).

```python run
def make_experiment(seed=77, n_per_group=12_000, lift_logodds=0.12, aov_factor_B=0.97):
    rng = np.random.default_rng(seed)
    n = 2 * n_per_group
    variant = np.repeat(["A", "B"], n_per_group)
    rng.shuffle(variant)                                                   # the coin flip: random assignment
    z = rng.normal(0, 1, n)                                                # latent keenness to buy (unobserved)
    pre_orders = rng.poisson(np.exp(0.9 * z))                       # observed: orders in the 90 days before the test
    logit = -3.1 + 1.0 * z + lift_logodds * (variant == "B")              # TRUTH: B raises the log-odds by 0.12
    converted = rng.random(n) < 1 / (1 + np.exp(-logit))
    revenue = np.where(converted, np.exp(rng.normal(6.7 + 0.3 * z, .4)) * np.where(variant == "B", aov_factor_B, 1.0), 0.0).round(0)
    day = pd.Timestamp("2024-11-04") + pd.to_timedelta(rng.integers(0, 14, n), unit="D")
    device = rng.choice(["mobile", "desktop"], n, p=[.65, .35])
    return pd.DataFrame({"visitor_id": np.arange(n), "day": day, "variant": variant, "device": device,
                         "pre_orders_90d": pre_orders, "converted": converted, "revenue": revenue})


exp = make_experiment()
print(exp.shape, "| grain: one row per visitor")
print(exp.head(3).to_string(index=False))
print(exp.groupby("variant")[["converted", "revenue", "pre_orders_90d"]].mean().round(3).to_string())
```
```text
(24000, 7) | grain: one row per visitor
 visitor_id        day variant device  pre_orders_90d  converted  revenue
          0 2024-11-08       A mobile               1      False     0.00
          1 2024-11-12       A mobile               0      False     0.00
          2 2024-11-17       A mobile               1      False     0.00
         converted  revenue  pre_orders_90d
variant                                    
A             0.06    74.87            1.50
B             0.07    79.40            1.50
```

### 2.4 Step 5: check the randomisation first

Before looking at any effect, check that the experiment is **valid**. Two checks catch most failures.

**The sample ratio check.** We asked for a 50/50 split. If the groups are 12,000 and 11,100, something broke: a bug dropped visitors from one arm, or a redirect lost some. A chi-square test compares the observed split with the intended one; a tiny p-value is a **sample ratio mismatch** (SRM), and it means *do not trust the experiment*, because whoever was lost was probably not random.

```python run
def srm_check(counts, expected_share=(0.5, 0.5)):
    counts = np.asarray(counts, float)
    exp_counts = counts.sum() * np.asarray(expected_share)
    chi2, p = stats.chisquare(counts, exp_counts)
    return chi2, p


c = exp["variant"].value_counts().sort_index()
chi2, p = srm_check(c.to_numpy())
print(f"our test:  A = {c['A']:,}, B = {c['B']:,} | chi-square {chi2:.2f}, p = {p:.3f} -> {'MISMATCH' if p < 0.001 else 'ok'}")
chi2b, pb = srm_check([12_000, 11_100])
print(f"a broken test: A = 12,000, B = 11,100 | chi-square {chi2b:.1f}, p = {pb:.1e} -> {'MISMATCH' if pb < 0.001 else 'ok'}")
```
```text
our test:  A = 12,000, B = 12,000 | chi-square 0.00, p = 1.000 -> ok
a broken test: A = 12,000, B = 11,100 | chi-square 35.1, p = 3.2e-09 -> MISMATCH
```

Our test passes (exactly 12,000 each by construction). A split of 12,000 against 11,100 looks like a small difference but its p-value is about 1e-9: with that many visitors, an 8 percent loss from one arm cannot be chance. The usual alarm threshold for SRM is a strict p < 0.001, because it is run on every experiment. The rule: **an experiment with an SRM is not analysed; it is debugged.**

**Balance on pre-experiment variables.** If randomisation worked, visitors in A and B should look alike *before* the test: same devices, same earlier purchasing.

```python run
print(exp.groupby("variant").agg(visitors=("visitor_id", "size"), mobile_share=("device", lambda s: (s == "mobile").mean()),
                                 pre_orders=("pre_orders_90d", "mean")).round(3).to_string())
t = stats.ttest_ind(exp.loc[exp["variant"] == "A", "pre_orders_90d"], exp.loc[exp["variant"] == "B", "pre_orders_90d"], equal_var=False)
print(f"difference in pre-experiment orders: p = {t.pvalue:.2f} (a large p-value means the groups look alike)")
```
```text
         visitors  mobile_share  pre_orders
variant                                    
A           12000          0.65        1.50
B           12000          0.65        1.50
difference in pre-experiment orders: p = 0.99 (a large p-value means the groups look alike)
```

The groups are alike on devices and on earlier orders. (If you test 20 such variables, expect one p below 0.05 by luck: da.08's multiple-comparisons warning applies to balance checks too.)

### 2.5 Step 6: the primary metric

Now the analysis, in the form of da.08: an effect with an interval, then a decision against the minimum effect.

```python run
def two_prop(kA, nA, kB, nB, level=0.95):
    pA, pB = kA / nA, kB / nB
    diff = pB - pA
    se = np.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    pp = (kA + kB) / (nA + nB)
    z_stat = diff / np.sqrt(pp * (1 - pp) * (1 / nA + 1 / nB))
    return {"A": pA, "B": pB, "diff": diff, "lo": diff - z * se, "hi": diff + z * se, "rel_lift": diff / pA, "p": 2 * (1 - stats.norm.cdf(abs(z_stat)))}


g = exp.groupby("variant")["converted"].agg(["sum", "size"])
res = two_prop(g.loc["A", "sum"], g.loc["A", "size"], g.loc["B", "sum"], g.loc["B", "size"])
print(f"conversion A {res['A'] * 100:.2f}% | B {res['B'] * 100:.2f}%")
print(f"difference {res['diff'] * 100:+.2f} points, 95% CI {res['lo'] * 100:+.2f} to {res['hi'] * 100:+.2f}  | relative lift {res['rel_lift'] * 100:+.1f}%  | p = {res['p']:.3f}")
MDE = 0.005
print("verdict against the minimum effect of +0.5 points:",
      "whole interval above" if res["lo"] > MDE else "whole interval below" if res["hi"] < MDE else "the interval contains the minimum effect: inconclusive about whether it pays")
```
```text
conversion A 6.36% | B 6.71%
difference +0.35 points, 95% CI -0.28 to +0.98  | relative lift +5.5%  | p = 0.273
verdict against the minimum effect of +0.5 points: the interval contains the minimum effect: inconclusive about whether it pays
```

In this test, B converted 6.71 percent against 6.36 percent for A: a difference of **+0.35 points** (a relative lift of 5.5 percent). The p-value is 0.27: **not significant**, and the interval, from -0.28 to +0.98 points, **contains zero and also contains the 0.5-point threshold**. The honest reading is the one of da.08: *the data are compatible with no effect and with a useful effect; this test cannot tell them apart.* It does **not** say the banner does nothing. (We happen to know that it does: the true lift is about +0.7 points. The test was too small to see it reliably, which is the whole point of the power calculation. Section 2.12 repeats the test many times to show how luck decides what a single underpowered test says.)

### 2.6 Guardrails and revenue per visitor

A banner that raises conversion but shrinks the basket might not raise revenue. The **guardrail** metrics check for harm. Average order value is a *continuous, skewed* variable among converters only; the better primary-style metric for the business is **revenue per visitor**, which combines both effects.

```python run
conv = exp[exp["converted"]]
aov = conv.groupby("variant")["revenue"].agg(["size", "mean", "std"])
print(aov.round(1).to_string())
t_aov = stats.ttest_ind(conv.loc[conv["variant"] == "B", "revenue"], conv.loc[conv["variant"] == "A", "revenue"], equal_var=False)
ci_aov = t_aov.confidence_interval(0.95)
print(f"AOV difference (B - A) {conv.loc[conv['variant'] == 'B', 'revenue'].mean() - conv.loc[conv['variant'] == 'A', 'revenue'].mean():+.0f} rupees, 95% CI {ci_aov.low:+.0f} to {ci_aov.high:+.0f}")


def mean_diff_ci(a, b, n_boot=4000, seed=1):
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    boots = np.array([rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(n_boot)])
    return b.mean() - a.mean(), np.quantile(boots, [.025, .975])


rA, rB = exp.loc[exp["variant"] == "A", "revenue"], exp.loc[exp["variant"] == "B", "revenue"]
d_rpv, ci_rpv = mean_diff_ci(rA, rB)
print(f"revenue per visitor: A {rA.mean():.2f}  B {rB.mean():.2f}  difference {d_rpv:+.2f} (bootstrap 95% CI {ci_rpv[0]:+.2f} to {ci_rpv[1]:+.2f})")
print(f"relative: {d_rpv / rA.mean() * 100:+.1f}%")
```
```text
         size     mean    std
variant                      
A         763 1,177.50 574.90
B         805 1,183.60 626.40
AOV difference (B - A) +6 rupees, 95% CI -53 to +66
revenue per visitor: A 74.87  B 79.40  difference +4.53 (bootstrap 95% CI -3.55 to +12.70)
relative: +6.0%
```

The average order value of the converters is about the same in the two groups (+6 rupees, with an interval from -53 to +66): no sign of harm from this guardrail, but a small decline (the true effect is -3 percent) would not be visible in a test this size. The net effect, **revenue per visitor**, is the number that matters for the shop. Revenue per visitor is a mean of mostly zeros and a skewed tail: the bootstrap is the honest tool for its interval (da.08), and here the interval is wide: from a loss of about 3.5 to a gain of 12.7 rupees per visitor. The summary of metrics so far:

| Metric | Result | Reading |
|---|---|---|
| Conversion (primary) | +0.35 points, CI -0.28 to +0.98, p = 0.27 | inconclusive: contains 0 and the 0.5-point threshold |
| Average order value (guardrail) | +6 rupees, CI -53 to +66 | no sign of harm; too imprecise to rule out a small decline |
| Revenue per visitor | +4.5 rupees (+6%), CI -3.5 to +12.7 | consistent with a gain, not established |

### 2.7 Sharpening the estimate: CUPED

The interval is wide because visitors vary a lot in how likely they are to buy. Some of that variation is **predictable from before the test**: visitors who ordered often in the previous 90 days buy more now. A technique called **CUPED** (controlled-experiment using pre-experiment data) subtracts the part of the outcome that the pre-experiment variable explains. Because the pre-experiment variable was measured *before* randomisation, it cannot be affected by the banner, so the adjustment is safe: it reduces noise without adding bias.

```text
adjusted outcome = outcome - theta x (pre-experiment value - its overall mean)
theta = covariance(outcome, pre) / variance(pre)
variance reduction = correlation(outcome, pre)^2
```

```python run
def cuped(df, y="converted", x="pre_orders_90d"):
    yv, xv = df[y].astype(float).to_numpy(), df[x].astype(float).to_numpy()
    theta = np.cov(yv, xv)[0, 1] / np.var(xv, ddof=1)
    return yv - theta * (xv - xv.mean()), theta, np.corrcoef(yv, xv)[0, 1] ** 2


exp["conv_adj"], theta, r2 = cuped(exp)
a_, b_ = exp.loc[exp["variant"] == "A", "conv_adj"], exp.loc[exp["variant"] == "B", "conv_adj"]
d_adj = b_.mean() - a_.mean()
se_raw = np.sqrt(exp.loc[exp["variant"] == "A", "converted"].var(ddof=1) / 12000 + exp.loc[exp["variant"] == "B", "converted"].var(ddof=1) / 12000)
se_adj = np.sqrt(a_.var(ddof=1) / 12000 + b_.var(ddof=1) / 12000)
print(f"correlation^2 between the outcome and pre-experiment orders: {r2:.3f}   (variance reduction)")
print(f"raw:   {res['diff'] * 100:+.2f} points, 95% CI {(res['diff'] - 1.96 * se_raw) * 100:+.2f} to {(res['diff'] + 1.96 * se_raw) * 100:+.2f}  (width {2 * 1.96 * se_raw * 100:.2f})")
print(f"CUPED: {d_adj * 100:+.2f} points, 95% CI {(d_adj - 1.96 * se_adj) * 100:+.2f} to {(d_adj + 1.96 * se_adj) * 100:+.2f}  (width {2 * 1.96 * se_adj * 100:.2f})")
print(f"the interval is {(1 - se_adj / se_raw) * 100:.0f}% narrower")
```
```text
correlation^2 between the outcome and pre-experiment orders: 0.049   (variance reduction)
raw:   +0.35 points, 95% CI -0.28 to +0.98  (width 1.25)
CUPED: +0.35 points, 95% CI -0.26 to +0.96  (width 1.22)
the interval is 2% narrower
```

The CUPED interval is only about 2 percent narrower here. The reason is in the printed line: the pre-experiment variable explains only 5 percent of the variance of a rare yes/no outcome (correlation squared of 0.049), and the interval width shrinks by a factor of `sqrt(1 - correlation^2)`. The method is not magic; it is only as good as the pre-experiment variable. How much it can give depends on the correlation:

```python run
print("correlation between outcome and the pre-experiment value -> how much narrower the interval gets")
for rho in (0.2, 0.5, 0.7, 0.9):
    print(f"  rho = {rho:.1f}: {(1 - np.sqrt(1 - rho ** 2)) * 100:4.0f}% narrower  (equivalent to {1 / (1 - rho ** 2):.1f}x the sample size)")
```
```text
correlation between outcome and the pre-experiment value -> how much narrower the interval gets
  rho = 0.2:    2% narrower  (equivalent to 1.0x the sample size)
  rho = 0.5:   13% narrower  (equivalent to 1.3x the sample size)
  rho = 0.7:   29% narrower  (equivalent to 2.0x the sample size)
  rho = 0.9:   56% narrower  (equivalent to 5.3x the sample size)
```

CUPED shines for **continuous, strongly persistent metrics** such as spend or sessions, where the previous period predicts the next with a correlation of 0.5 to 0.8 and the interval narrows by a seventh to a third, which is like collecting up to twice the data for free. Here is the same adjustment on revenue per visitor:

```python run
exp["pre_spend_proxy"] = exp["pre_orders_90d"] * 800.0                        # the pre-period order count as a proxy for pre-period spend
exp["rev_adj"], theta_r, r2_r = cuped(exp, y="revenue", x="pre_orders_90d")
ra, rb = exp.loc[exp["variant"] == "A", "rev_adj"], exp.loc[exp["variant"] == "B", "rev_adj"]
se_r_raw = np.sqrt(rA.var(ddof=1) / 12000 + rB.var(ddof=1) / 12000)
se_r_adj = np.sqrt(ra.var(ddof=1) / 12000 + rb.var(ddof=1) / 12000)
print(f"revenue per visitor: correlation^2 with pre-experiment orders = {r2_r:.3f}")
print(f"  raw  : {d_rpv:+.2f}, 95% CI {d_rpv - 1.96 * se_r_raw:+.2f} to {d_rpv + 1.96 * se_r_raw:+.2f}")
print(f"  CUPED: {rb.mean() - ra.mean():+.2f}, 95% CI {rb.mean() - ra.mean() - 1.96 * se_r_adj:+.2f} to {rb.mean() - ra.mean() + 1.96 * se_r_adj:+.2f}")
print(f"  the interval is {(1 - se_r_adj / se_r_raw) * 100:.0f}% narrower")
```
```text
revenue per visitor: correlation^2 with pre-experiment orders = 0.082
  raw  : +4.53, 95% CI -3.82 to +12.87
  CUPED: +4.51, 95% CI -3.48 to +12.50
  the interval is 4% narrower
```

A modest gain again (about 4 percent), because the count of orders in 90 days is a weak predictor of one fortnight's spend. A useful rule: compute the correlation first; if it is below about 0.3, CUPED is not worth the extra step.

### 2.8 Peeking and stopping early

The most tempting mistake in A/B testing is to **look at the result every day and stop as soon as it is significant**. Each look is another chance for luck to cross the 0.05 line. We can measure the damage with an **A/A simulation**: both groups have the *same* conversion rate (no effect at all), and we apply two procedures.

```python run
def peeking_simulation(n_sims=1500, n_per_group=12000, looks=14, p=0.06, seed=3):
    rng = np.random.default_rng(seed)
    fixed_hits = peek_hits = 0
    per_look = n_per_group // looks
    for _ in range(n_sims):
        a = rng.random(n_per_group) < p
        b = rng.random(n_per_group) < p
        sig_any = False
        for k in range(1, looks + 1):
            n = per_look * k
            ka, kb = a[:n].sum(), b[:n].sum()
            pp = (ka + kb) / (2 * n)
            z = (kb - ka) / n / np.sqrt(pp * (1 - pp) * 2 / n)
            if abs(z) > 1.96:
                sig_any = True
        peek_hits += sig_any
        n = per_look * looks
        ka, kb = a[:n].sum(), b[:n].sum()
        pp = (ka + kb) / (2 * n)
        z = (kb - ka) / n / np.sqrt(pp * (1 - pp) * 2 / n)
        fixed_hits += abs(z) > 1.96
    return fixed_hits / n_sims, peek_hits / n_sims


fixed, peek = peeking_simulation()
print(f"false positive rate with ONE look at the planned end : {fixed * 100:.1f}%  (the promised 5%)")
print(f"false positive rate if you stop at the first significant daily look (14 looks): {peek * 100:.1f}%")
```
```text
false positive rate with ONE look at the planned end : 5.5%  (the promised 5%)
false positive rate if you stop at the first significant daily look (14 looks): 21.3%
```

Checking every day and stopping on the first "significant" result turns a 5 percent false-alarm rate into about **21 percent**: about one A/A test in five would be declared a winner when nothing changed. The remedies: fix the sample size and the end date in advance and analyse once; or use a **sequential testing** method designed for repeated looks (the boundaries are stricter early on); or at least require the full planned duration. Looking at the dashboard is allowed; **deciding** from it before the end is not.

### 2.9 Other things that go wrong

| Problem | What happens | What to do |
|---|---|---|
| **Underpowered test** | a real effect is missed, or the interval is too wide to decide | calculate the sample size first; report the interval |
| **Peeking** | many false positives | fixed horizon or sequential methods |
| **Whole weeks** | weekday effects bias a test that ends mid-week | run in complete weeks (7, 14, 21 days) |
| **Novelty effect** | users click a new thing because it is new; the lift fades | run long enough; compare early and late days |
| **Many metrics, many segments** | one will be "significant" by luck | one primary metric; pre-registered segments; correct for multiplicity |
| **Interference** | users affect each other (shared carts, social features) | randomise by group, region or time block |
| **Sample ratio mismatch** | the experiment is invalid | stop and debug before any analysis |
| **Changing the test while it runs** | the groups are no longer comparable | freeze the design |
| **Treating "not significant" as "no effect"** | a good idea is dropped | read the interval against the minimum effect |

A quick check for a **novelty effect** in our data: does the lift look the same in the first week and the second?

```python run
exp["week"] = np.where(exp["day"] < "2024-11-11", "week 1", "week 2")
rows = []
for wk, sub in exp.groupby("week"):
    g = sub.groupby("variant")["converted"].agg(["sum", "size"])
    r = two_prop(g.loc["A", "sum"], g.loc["A", "size"], g.loc["B", "sum"], g.loc["B", "size"])
    rows.append({"week": wk, "n per group": int(g.loc["A", "size"]), "A %": r["A"] * 100, "B %": r["B"] * 100, "diff (points)": r["diff"] * 100,
                 "CI low": r["lo"] * 100, "CI high": r["hi"] * 100})
print(pd.DataFrame(rows).round(2).to_string(index=False))
```
```text
  week  n per group  A %  B %  diff (points)  CI low  CI high
week 1         6033 6.35 6.94           0.59   -0.30     1.48
week 2         5967 6.37 6.48           0.11   -0.77     0.99
```

The lift is larger in the first week (+0.59 points) than in the second (+0.11), which is the pattern a novelty effect would produce. But look at the intervals: both are wide and overlap almost completely (-0.30 to +1.48 against -0.77 to +0.99), so the difference between the weeks is well within noise. The right reading is "a possible sign of a novelty effect, which this test cannot confirm or exclude". In practice you would **extend the test** and watch whether the lift settles, rather than conclude either way from fourteen days.

### 2.10 Segments: look, but do not decide on them

"Does the banner work better on mobile?" is a natural question and a dangerous one. Every segment you check is another comparison; the result of a segment is noisier (smaller `n`); and a difference between segments needs its own test (an **interaction**), not just two separate "significant / not significant" labels.

```python run
rows = []
for dev, sub in exp.groupby("device"):
    g = sub.groupby("variant")["converted"].agg(["sum", "size"])
    r = two_prop(g.loc["A", "sum"], g.loc["A", "size"], g.loc["B", "sum"], g.loc["B", "size"])
    rows.append({"device": dev, "n per group": int(g.loc["A", "size"]), "A %": r["A"] * 100, "B %": r["B"] * 100,
                 "diff (points)": r["diff"] * 100, "CI low": r["lo"] * 100, "CI high": r["hi"] * 100})
seg = pd.DataFrame(rows)
print(seg.round(2).to_string(index=False))
m = sm.Logit(exp["converted"].astype(float), sm.add_constant(pd.DataFrame({"B": (exp["variant"] == "B").astype(float), "mobile": (exp["device"] == "mobile").astype(float)}).assign(B_x_mobile=lambda d: d["B"] * d["mobile"]))).fit(disp=False)
print(f"\ninteraction (does the effect differ by device?): coefficient {m.params['B_x_mobile']:+.3f}, p = {m.pvalues['B_x_mobile']:.2f}")
```
```text
 device  n per group  A %  B %  diff (points)  CI low  CI high
desktop         4218 6.59 6.33          -0.27   -1.31     0.78
 mobile         7782 6.23 6.92           0.68   -0.09     1.46

interaction (does the effect differ by device?): coefficient +0.155, p = 0.16
```

Mobile looks better (+0.68 points, an interval that nearly excludes zero) and desktop shows nothing (-0.27, interval spanning zero). A tempting headline: "the banner works on mobile". Do not write it. The difference between the segments is tested by the **interaction** term, and its p-value is 0.16: no reliable difference. "Significant in one segment, not in the other" is not a test that the segments differ (the mobile group is simply twice as large, so its interval is narrower). A segment split is a **hypothesis for the next test**, not a result; do not roll the banner out to mobile only on this evidence.

### 2.11 The decision

The decision rule is in da.08's terms, but with the money counted properly: extra **revenue** is not extra **profit**. Only the **contribution** (revenue times the margin) pays for the shipping subsidy. The finance team gives two assumptions: a 30 percent contribution margin, and a cost of 25 rupees of extra shipping for every converted visitor in group B (the subsidy applies to everybody who buys, including those who would have bought anyway).

```python run
MARGIN = 0.30                                         # contribution margin (assumption from finance)
SHIP_SUBSIDY = 25                                     # extra shipping cost per converted visitor in B (assumption from finance)
visitors_per_month = 1700 * 30
conv_B = exp.loc[exp["variant"] == "B", "converted"].mean()
cost = conv_B * visitors_per_month * SHIP_SUBSIDY
gain_lo, gain_hi, gain_mid = (x * visitors_per_month for x in (ci_rpv[0], ci_rpv[1], d_rpv))          # extra REVENUE a month
print(f"extra revenue a month for {visitors_per_month:,} cart visitors: {gain_mid:+,.0f} (range {gain_lo:+,.0f} to {gain_hi:+,.0f})")
print(f"shipping subsidy a month: {cost:,.0f} rupees")
net = lambda g: g * MARGIN - cost
print(f"net contribution: {net(gain_mid):+,.0f} a month (range {net(gain_lo):+,.0f} to {net(gain_hi):+,.0f})")
breakeven = cost / visitors_per_month / MARGIN
print(f"break-even: the banner pays only if revenue per visitor rises by more than {breakeven:.1f} rupees (observed {d_rpv:+.1f}, CI {ci_rpv[0]:+.1f} to {ci_rpv[1]:+.1f})")
print(f"for comparison, +0.5 points of conversion at the average order value is worth {0.005 * conv[conv['variant'] == 'A']['revenue'].mean():.1f} rupees per visitor")
AB = {"conv_diff_pts": res["diff"] * 100, "conv_lo": res["lo"] * 100, "conv_hi": res["hi"] * 100, "conv_p": res["p"],
      "rpv": d_rpv, "rpv_lo": float(ci_rpv[0]), "rpv_hi": float(ci_rpv[1]), "net_mid": net(gain_mid), "net_lo": net(gain_lo), "net_hi": net(gain_hi),
      "breakeven_rpv": breakeven, "n_per_group_needed": n_per_group(0.06, MDE)}                              # saved for the recommendation in section 6
```
```text
extra revenue a month for 51,000 cart visitors: +230,830 (range -181,035 to +647,476)
shipping subsidy a month: 85,531 rupees
net contribution: -16,282 a month (range -139,842 to +108,712)
break-even: the banner pays only if revenue per visitor rises by more than 5.6 rupees (observed +4.5, CI -3.5 to +12.7)
for comparison, +0.5 points of conversion at the average order value is worth 5.9 rupees per visitor
```

The break-even line explains where the "0.5-point minimum effect" of 2.2 came from: +0.5 points of conversion is worth about 6 rupees per visitor, which is about the break-even of 5.6. So the minimum effect was not arbitrary: it is the lift at which the banner pays for itself. The best estimate of the effect (+4.5 rupees per visitor) is **below** break-even, the net contribution is about zero (a loss of roughly 17,000 rupees a month at the best estimate), and the range runs from a loss of about 140,000 to a gain of about 110,000 rupees a month. A defensible decision: **do not roll out to everyone**. The evidence does not show that the banner pays; to settle the question the test would have to be extended (about 37,000 visitors per group), or a cheaper design tested instead (for example free shipping only above a basket threshold, so that the subsidy goes to baskets that need the push). That is a *recommendation with a range and a next step*, not "not significant, so drop it" and not "the lift is positive, so ship it". Section 6 puts this next to the other three answers.

### 2.12 What an underpowered test does: repeat it 400 times

We know the truth (the banner is worth about +0.7 points), so we can run the same 14-day test many times and see what a single test would have told us. Each row below is a whole experiment.

```python run
rows = []
for s in range(400):
    e = make_experiment(seed=1000 + s)
    g = e.groupby("variant")["converted"].agg(["sum", "size"])
    r = two_prop(g.loc["A", "sum"], g.loc["A", "size"], g.loc["B", "sum"], g.loc["B", "size"])
    rows.append(r)
sim = pd.DataFrame(rows)
print(f"estimated lift over 400 repeats: mean {sim['diff'].mean() * 100:+.2f} points (the truth is about +0.7), spread (SD) {sim['diff'].std() * 100:.2f} points")
print(f"central 90% of the estimates: {sim['diff'].quantile(.05) * 100:+.2f} to {sim['diff'].quantile(.95) * 100:+.2f} points")
print(f"tests with p < 0.05 (would be called a win): {(sim['p'] < .05).mean() * 100:.0f}%")
print(f"tests whose whole interval is above the 0.5-point threshold: {(sim['lo'] > MDE).mean() * 100:.0f}%")
print(f"tests whose whole interval is below 0.5 points (would say 'not worth it'): {(sim['hi'] < MDE).mean() * 100:.0f}%")
print(f"inconclusive (the interval contains 0.5 points): {((sim['lo'] <= MDE) & (sim['hi'] >= MDE)).mean() * 100:.0f}%")
print(f"estimates below zero (the banner would look harmful): {(sim['diff'] < 0).mean() * 100:.0f}%")
```
```text
estimated lift over 400 repeats: mean +0.69 points (the truth is about +0.7), spread (SD) 0.32 points
central 90% of the estimates: +0.15 to +1.23 points
tests with p < 0.05 (would be called a win): 57%
tests whose whole interval is above the 0.5-point threshold: 8%
tests whose whole interval is below 0.5 points (would say 'not worth it'): 0%
inconclusive (the interval contains 0.5 points): 92%
estimates below zero (the banner would look harmful): 2%
```

A single 14-day test of a banner that really works would have been called a win (p below 0.05) in only about **57 percent** of the repeats, would have looked harmful in 2 percent, and would have left the question "is it above the 0.5-point threshold?" **open in 92 percent**: only 8 percent of the tests could actually show that the lift is large enough to pay. The estimates are centred on the truth (the experiment is unbiased; the average is +0.69 points), but each one is a noisy draw with a spread of about 0.3 points. This is the reason to do the power calculation *before* the test, to plan for a larger sample, and to read every result through its interval. The lesson for the manager: "no significant result" is information about the *experiment*, not only about the idea.


## 3. Funnel analysis

### 3.1 The question

*Where do shoppers drop out between arriving and buying, and which leak is worth fixing first?* A **funnel** lists the steps of a process in order and counts how many visitors reach each one. You met funnels in SQL in da.07; here we do the analysis in pandas and add what the business needs: comparing groups, quantifying each leak, and ranking the possible fixes by their payoff.

The rules from da.07 still hold, and we restate them because they are where funnels go wrong. Count the **unit the question names** (here the *session*, not the event). Require the steps in **order**. Keep every visitor who entered the funnel, including those who left at the first step. Restrict to periods that are **complete**.

### 3.2 The session data

One month of shopping sessions on the site (November 2024), 60,000 of them. For each session we know the channel it arrived from, the device, and the furthest step it reached. We planted two facts to find: **mobile shoppers leak at the checkout step** (they start checkout far less often after adding to the cart), and email traffic is simply better.

```python run
def make_sessions(seed=5, n=60_000):
    rng = np.random.default_rng(seed)
    channel = rng.choice(["organic", "paid", "email", "referral"], n, p=[.42, .38, .12, .08])
    mobile_p = pd.Series(channel).map({"organic": .62, "paid": .78, "email": .70, "referral": .60}).to_numpy()
    device = np.where(rng.random(n) < mobile_p, "mobile", "desktop")                 # paid traffic is mostly mobile: a mix effect to watch
    view = rng.random(n) < pd.Series(channel).map({"organic": .66, "paid": .55, "email": .72, "referral": .70}).to_numpy()
    cart = view & (rng.random(n) < pd.Series(channel).map({"organic": .30, "paid": .28, "email": .36, "referral": .33}).to_numpy())
    checkout = cart & (rng.random(n) < np.where(device == "mobile", .45, .66))          # TRUTH: the mobile checkout leak
    buy = checkout & (rng.random(n) < np.where(device == "mobile", .70, .76))
    amount = np.where(buy, np.exp(rng.normal(6.7, .35, n)), 0).round(0)
    day = pd.Timestamp("2024-11-01") + pd.to_timedelta(rng.integers(0, 30, n), unit="D")
    return pd.DataFrame({"session_id": np.arange(n), "day": day, "channel": channel, "device": device,
                         "viewed_product": view, "added_to_cart": cart, "started_checkout": checkout, "purchased": buy, "amount": amount})


sessions = make_sessions()
STEPS = ["viewed_product", "added_to_cart", "started_checkout", "purchased"]
print(sessions.shape, "| grain: one row per session")
print(sessions.head(3).to_string(index=False))
# the funnel must be ordered: no one can reach a step without the one before it
ordered = all(((sessions[b] & ~sessions[a]).sum() == 0) for a, b in zip(STEPS[:-1], STEPS[1:]))
print("steps are nested (nobody reaches a step without the previous one):", ordered)
```
```text
(60000, 9) | grain: one row per session
 session_id        day channel device  viewed_product  added_to_cart  started_checkout  purchased  amount
          0 2024-11-08   email mobile            True           True              True       True  764.00
          1 2024-11-05   email mobile            True          False             False      False    0.00
          2 2024-11-24    paid mobile            True          False             False      False    0.00
steps are nested (nobody reaches a step without the previous one): True
```

The nesting check is an audit of the tracking: if a session had `purchased` without `started_checkout`, the funnel would be unordered (like the direct-link buyers of da.07), and we would have to decide how to count them. Here the steps are nested by construction.

### 3.3 The funnel table

```python run
def funnel_table(df, steps=STEPS):
    n = len(df)
    rows = [("sessions", n, np.nan, 100.0)]
    prev = n
    for s in steps:
        k = int(df[s].sum())
        rows.append((s, k, k / prev * 100, k / n * 100))
        prev = k
    t = pd.DataFrame(rows, columns=["step", "sessions", "% of previous step", "% of all sessions"])
    t["dropped"] = t["sessions"].shift(1) - t["sessions"]
    return t


ft = funnel_table(sessions)
print(ft.round(1).to_string(index=False))
print(f"\noverall conversion (session to purchase): {sessions['purchased'].mean() * 100:.2f}%")
```
```text
            step  sessions  % of previous step  % of all sessions   dropped
        sessions     60000                 NaN             100.00       NaN
  viewed_product     37545               62.60              62.60 22,455.00
   added_to_cart     11409               30.40              19.00 26,136.00
started_checkout      5848               51.30               9.70  5,561.00
       purchased      4251               72.70               7.10  1,597.00

overall conversion (session to purchase): 7.08%
```

The overall conversion is about 7 percent. The two columns say different things, and a good funnel reading uses both. "% of the previous step" shows where the **rate** of loss is highest: only 30 percent of the sessions that viewed a product add anything to the cart, and only 51 percent of carts start checkout. "Dropped" shows where the **most sessions** leave: the largest absolute loss is between viewing a product and adding it to the cart (26,000 sessions), then the sessions that never view a product (22,000). Not every leak can be fixed: people who browse and do not buy are normal. A step is a good target when its rate looks low *compared with a sensible benchmark* and a lot of traffic reaches it, which is what the segment cuts below let us test.

### 3.4 Compare segments, and beware of mix

The same funnel, cut by device and by channel. For each step we show the step conversion with an interval, because small groups are noisy (da.08).

```python run
def wilson(k, n, level=0.95):
    ci = stats.binomtest(int(k), int(n)).proportion_ci(level, method="wilson")
    return ci.low, ci.high


def step_rates(df, by):
    rows = []
    for key, g in df.groupby(by):
        prev = len(g)
        row = {by: key, "sessions": len(g)}
        for s in STEPS:
            k = int(g[s].sum())
            row[f"{s.split('_')[0]} %"] = k / prev * 100
            prev = k
        row["overall %"] = g["purchased"].mean() * 100
        rows.append(row)
    return pd.DataFrame(rows).set_index(by)


print(step_rates(sessions, "device").round(1).to_string())
print()
print(step_rates(sessions, "channel").round(1).to_string())
```
```text
         sessions  viewed %  added %  started %  purchased %  overall %
device                                                                 
desktop     18719     63.50    30.20      65.20        77.30       9.70
mobile      41281     62.10    30.50      44.90        69.60       5.90

          sessions  viewed %  added %  started %  purchased %  overall %
channel                                                                 
email         7037     71.80    35.60      51.00        71.40       9.30
organic      25182     65.90    30.10      52.20        74.50       7.70
paid         22917     54.60    28.10      49.50        69.80       5.30
referral      4864     69.70    32.60      52.90        75.30       9.00
```

Read the device table first. Desktop and mobile are the same at the first two steps (view, add to cart). At the third, "started checkout", desktop converts about 66 percent of its carts and mobile only about 45: **a big gap at exactly one step**. That is the leak. The channel table shows email and referral converting better overall, which is mostly a difference in the first two steps and in the share of mobile traffic.

That last point is a **mix effect** (da.06, da.10), and it can mislead: paid traffic converts worst *and* is mostly mobile; is the problem the channel or the device? A cross-tab separates them.

```python run
x = sessions.groupby(["channel", "device"]).agg(sessions=("purchased", "size"), cart=("added_to_cart", "sum"), checkout=("started_checkout", "sum"), bought=("purchased", "sum"))
x["cart->checkout %"] = x["checkout"] / x["cart"] * 100
x["overall %"] = x["bought"] / x["sessions"] * 100
print(x[["sessions", "cart->checkout %", "overall %"]].round(1).to_string())
```
```text
                  sessions  cart->checkout %  overall %
channel  device                                        
email    desktop      2098             65.60      12.40
         mobile       4939             44.90       8.00
organic  desktop      9558             65.10      10.10
         mobile      15624             44.30       6.20
paid     desktop      5127             66.10       7.20
         mobile      17790             45.20       4.80
referral desktop      1936             63.80      11.00
         mobile       2928             45.90       7.80
```

Inside **every channel**, the mobile "cart to checkout" rate is about 20 points below desktop (45 against 66), while the channel differences at that step are small. So the checkout leak is a **device** problem that affects every channel; the apparent weakness of paid traffic is partly because paid is 78 percent mobile. Fixing mobile checkout would help every channel, paid most.

### 3.5 Size the opportunity

A leak matters according to **how many orders it costs**. The question for the product team is "what would we gain if we closed it?", and the honest answer comes with an interval. If mobile sessions converted from cart to checkout at the desktop rate, how many more orders and how much revenue would there be?

```python run
def opportunity(df, target_rate, n_boot=2000, seed=2):
    """Extra purchases if the mobile cart->checkout rate rose to `target_rate`, holding the later steps as they are."""
    m = df[df["device"] == "mobile"]
    carts = int(m["added_to_cart"].sum())
    chk = m[m["added_to_cart"]]["started_checkout"]
    pay_rate = m[m["started_checkout"]]["purchased"].mean()                  # checkout -> purchase on mobile
    aov = df.loc[df["purchased"], "amount"].mean()
    rng = np.random.default_rng(seed)
    extra = []
    for _ in range(n_boot):
        c = rng.choice(chk.to_numpy(), len(chk))
        extra.append((target_rate - c.mean()) * carts * pay_rate)
    extra = np.array(extra)
    return carts, chk.mean(), pay_rate, aov, extra


desk = sessions[(sessions["device"] == "desktop") & sessions["added_to_cart"]]["started_checkout"].mean()
carts, now_rate, pay_rate, aov, extra = opportunity(sessions, desk)
lo, mid, hi = np.quantile(extra, [.025, .5, .975])
print(f"mobile carts in the month: {carts:,} | mobile cart->checkout now {now_rate * 100:.1f}% | desktop {desk * 100:.1f}% | mobile checkout->purchase {pay_rate * 100:.1f}%")
print(f"extra purchases a month if mobile matched desktop: {mid:,.0f} (95% interval {lo:,.0f} to {hi:,.0f})")
print(f"average order value {aov:,.0f} -> extra revenue {mid * aov:,.0f} a month ({lo * aov:,.0f} to {hi * aov:,.0f})")
print(f"that is {mid / sessions['purchased'].sum() * 100:.0f}% more orders than the {int(sessions['purchased'].sum()):,} of the month")
OPP = {"mid": float(mid), "lo": float(lo), "hi": float(hi), "aov": float(aov), "now_rate": float(now_rate), "desk_rate": float(desk)}      # saved for section 6
```
```text
mobile carts in the month: 7,819 | mobile cart->checkout now 44.9% | desktop 65.2% | mobile checkout->purchase 69.6%
extra purchases a month if mobile matched desktop: 1,107 (95% interval 1,048 to 1,168)
average order value 861 -> extra revenue 953,243 a month (902,290 to 1,005,379)
that is 26% more orders than the 4,251 of the month
```

Closing the gap entirely would bring about 1,100 extra orders a month (roughly a quarter more orders), worth around 950,000 rupees. The narrow interval (about 1,050 to 1,170) covers only the sampling noise of today's mobile rate; the much larger uncertainty is whether a redesign could reach the desktop rate at all. **That is a ceiling**, not a forecast: nobody expects a redesign to make mobile checkout exactly as good as desktop, so the plan should assume part of it (say a third to a half). Compare the alternatives on the same scale:

```python run
base_orders = int(sessions["purchased"].sum())
cands = []
v = sessions["viewed_product"].sum()
cands.append(("raise view->cart by 10% (relative), all traffic", .10 * base_orders))                  # every later step unchanged, so orders rise 10%
cands.append(("raise checkout->purchase by 5% (relative), all traffic", .05 * sessions["purchased"].sum()))
cands.append(("raise mobile cart->checkout to the desktop level", mid))
cands.append(("raise mobile cart->checkout halfway to desktop", mid / 2))
op = pd.DataFrame(cands, columns=["idea", "extra orders a month"])
op["% more orders"] = op["extra orders a month"] / base_orders * 100
op["extra revenue"] = op["extra orders a month"] * aov
print(op.round(1).to_string(index=False))
```
```text
                                                  idea  extra orders a month  % more orders  extra revenue
       raise view->cart by 10% (relative), all traffic                425.10          10.00     365,997.70
raise checkout->purchase by 5% (relative), all traffic                212.60           5.00     182,998.80
      raise mobile cart->checkout to the desktop level              1,107.20          26.00     953,242.60
        raise mobile cart->checkout halfway to desktop                553.60          13.00     476,621.30
```

On this simple scale the mobile-checkout fix is the largest single opportunity: even half of it beats a 5 percent improvement of the last step across all traffic. The ranking is only part of a decision (a fix also has a cost and a risk), but it replaces "mobile checkout feels bad" with "mobile checkout is worth roughly 550 to 1,100 orders a month", and that is how a team chooses what to build next.

> **Try it.** The product team thinks a redesign could lift the mobile cart-to-checkout rate to 55 percent (not all the way to desktop's 65). How many extra orders a month is that worth, using the same logic as above?

<details><summary>Answer</summary>

```python run
extra_55 = (0.55 - OPP["now_rate"]) * carts * pay_rate
print(f"to 55%: {extra_55:,.0f} extra orders a month ({extra_55 * aov:,.0f} rupees), i.e. {extra_55 / OPP['mid'] * 100:.0f}% of the full gap")
```
```text
to 55%: 552 extra orders a month (475,487 rupees), i.e. 50% of the full gap
```

About 550 extra orders a month, half of the ceiling. Because the effect is linear in the target rate, a table of targets (50, 55, 60, 65 percent) gives the product team the whole range in four lines, and the funnel analysis becomes a planning tool rather than a diagnosis.

</details>

### 3.6 From funnel to experiment

A funnel tells you **where** to look and **how big** the prize is. It cannot tell you that a particular fix **works**: that needs an experiment (section 2). The workflow is therefore: funnel analysis finds the leak and sizes it; the team proposes a redesign; an A/B test with a power calculation (the minimum effect comes from the opportunity table) tests it. And the funnel is the natural **diagnostic** for the test: if the banner of section 2 worked, the step "cart to checkout" should be where it shows up.

### 3.7 Funnel pitfalls

| Pitfall | What goes wrong | What to do |
|---|---|---|
| Counting events, not sessions or users | repeated page views inflate step 1 | count the unit of the question (da.07) |
| Unordered steps | skippers and tracking gaps counted | check that steps are nested; decide how to treat exceptions |
| Dropping people who left at step 1 | a funnel that starts at step 2 | start from everyone who entered |
| Different time windows per step | long consideration looks like abandonment | define a conversion window; use complete periods |
| Comparing channels without device mix | a device effect read as a channel effect | cross-tabs; decomposition (da.10) |
| Tiny segments | noisy rates | show `n` and intervals |
| Reading the funnel as causal | "fix the biggest drop and conversions rise" | size with intervals, then test |

## 4. Cohorts, retention and customer value

### 4.1 The questions

*Do customers from each channel come back, and what is a customer worth?* These questions need **time**: a customer's value is the stream of orders after the first, and a cohort is the right lens (da.07's cohort matrix, now in pandas). A **cohort** groups customers by when they were acquired (here: the month of their first order). **Retention** asks what share of each cohort is *still buying* `k` months later. **Customer lifetime value** (LTV) adds up what they bring.

Definitions, in the style of da.06 (write the definition before computing):

| Term | Definition in this chapter |
|---|---|
| Cohort | month of the customer's first order |
| Active in month `k` | at least one order in the calendar month that is `k` months after the cohort month |
| Retention(k) | distinct active customers in month `k` / cohort size |
| Mature cell | month `cohort + k` is on or before December 2024 (the last complete month) |
| Repeat rate within 90 days | share of customers with a second order within 90 days of the first, among customers observed for at least 90 days |
| 12-month revenue | revenue in the first 365 days from the first order, for customers observed for a full 365 days |

The two "observed for at least..." rules are the immature-cohort rules of da.07: a customer acquired in November 2024 cannot show a 90-day repeat rate yet, and counting them as "did not return" would pull every rate down.

### 4.2 The retention matrix

```python run
o = orders.merge(customers[["customer_id", "first_order", "channel"]], on="customer_id", how="left", validate="m:1")
o["cohort"] = o["first_order"].dt.to_period("M")
o["month"] = o["order_date"].dt.to_period("M")
o["k"] = (o["order_date"].dt.year - o["first_order"].dt.year) * 12 + (o["order_date"].dt.month - o["first_order"].dt.month)
cust_cohort = customers.assign(cohort=customers["first_order"].dt.to_period("M"))
size = cust_cohort.groupby("cohort").size()
active = o.groupby(["cohort", "k"])["customer_id"].nunique().unstack("k")
LAST = pd.Period("2024-12")
max_k = pd.Series({c: (LAST.year - c.year) * 12 + (LAST.month - c.month) for c in size.index})
ret = active.div(size, axis=0) * 100
for c in ret.index:                                                       # keep only mature cells: months that have happened
    ret.loc[c, ret.columns > max_k[c]] = np.nan
show = ret.loc[["2023-01", "2023-04", "2023-07", "2023-10", "2024-01", "2024-04", "2024-07"], [0, 1, 2, 3, 6, 9, 12]]
show.columns = [f"M{c}" for c in show.columns]
show.insert(0, "size", size.loc[show.index])
print(show.round(1).to_string())
print("\nM0 is 100% by definition (the first order). Cells that have not happened yet are empty (NaN), not 0.")
```
```text
         size     M0    M1    M2    M3    M6    M9   M12
cohort                                                  
2023-01   255 100.00 22.70 24.70 22.00 11.00 13.30  7.80
2023-04   256 100.00 29.30 21.10 19.50 17.60 12.10 11.30
2023-07   245 100.00 24.10 18.00 20.00 15.50 11.80 11.80
2023-10   267 100.00 25.10 22.80 19.50 15.40 12.00  9.00
2024-01   271 100.00 22.90 22.90 21.00 12.50 11.40   NaN
2024-04   274 100.00 25.20 25.90 21.50 23.40   NaN   NaN
2024-07   254 100.00 22.00 18.10 19.30   NaN   NaN   NaN

M0 is 100% by definition (the first order). Cells that have not happened yet are empty (NaN), not 0.
```

Read the matrix as in da.07: each row is a cohort, each column the months since acquisition. The shape is what retention curves always look like: a steep fall after the first month (many customers buy once and never again), then a flatter tail. The empty cells in the lower right are the months that have not happened for recent cohorts; they stay empty.

A check of the unit: `size` counts customers by first-order month, and each customer appears in exactly one cohort.

```python run
print("cohort sizes add up to the customers:", int(size.sum()) == len(customers), "| number of cohorts:", len(size))
print("customers whose first order is also counted as M0 activity:", bool((active[0] == size).all()))
```
```text
cohort sizes add up to the customers: True | number of cohorts: 24
customers whose first order is also counted as M0 activity: True
```

### 4.3 The average curve, and the channels

To compare channels we need a single curve per channel, pooled over cohorts. The right way (da.07 section 6.5): at each `k`, add the numerators and denominators over the customers who *can* have reached month `k`.

```python run
def pooled_retention(channel_filter=None, ks=(1, 2, 3, 6, 9, 12)):
    cu = customers if channel_filter is None else customers[customers["channel"] == channel_filter]
    cu = cu.assign(cohort=cu["first_order"].dt.to_period("M"))
    cu["maxk"] = cu["cohort"].map(max_k)
    oo = o[o["customer_id"].isin(cu["customer_id"])]
    rows = []
    for k in ks:
        elig = cu[cu["maxk"] >= k]
        act = oo[(oo["k"] == k) & oo["customer_id"].isin(elig["customer_id"])]["customer_id"].nunique()
        lo, hi = wilson(act, len(elig))
        rows.append({"k": k, "eligible": len(elig), "active": act, "retention %": act / len(elig) * 100, "CI low": lo * 100, "CI high": hi * 100})
    return pd.DataFrame(rows).set_index("k")


print("all customers")
print(pooled_retention().round(1).to_string())
```
```text
all customers
    eligible  active  retention %  CI low  CI high
k                                                 
1       5873    1436        24.50   23.40    25.60
2       5635    1278        22.70   21.60    23.80
3       5366    1106        20.60   19.60    21.70
6       4576     698        15.30   14.20    16.30
9       3773     472        12.50   11.50    13.60
12      2978     270         9.10    8.10    10.20
```

At each `k` only the customers with enough follow-up are counted, so the eligible number shrinks as `k` grows (fewer and older cohorts). The interval gets wider for the same reason. Now the channels at three points of the curve:

```python run
rows = []
for ch in ["organic", "paid", "email", "referral"]:
    t = pooled_retention(ch, ks=(1, 3, 6, 12))
    for k, r in t.iterrows():
        rows.append({"channel": ch, "k": k, "retention %": r["retention %"], "CI low": r["CI low"], "CI high": r["CI high"], "eligible": r["eligible"]})
chan = pd.DataFrame(rows)
print(chan.pivot(index="channel", columns="k", values="retention %").round(1).to_string())
print()
print("month 6, with intervals:")
print(chan[chan["k"] == 6].set_index("channel")[["retention %", "CI low", "CI high", "eligible"]].round(1).to_string())
```
```text
k           1     3     6     12
channel                         
email    28.80 30.90 21.30 11.40
organic  26.70 21.60 16.60 10.60
paid     17.30 12.50  8.20  3.40
referral 33.70 29.90 25.10 18.40

month 6, with intervals:
          retention %  CI low  CI high  eligible
channel                                         
organic         16.60   15.00    18.40  1,845.00
paid             8.20    7.00     9.70  1,581.00
email           21.30   18.40    24.50    695.00
referral        25.10   21.30    29.20    455.00
```

The order at month 6 is clear and the intervals separate: **referral and email** customers keep buying far longer than **paid** customers, with organic in between. Look at month 12, though: email falls to the level of organic (11 percent against 11 percent, with overlapping intervals), while referral stays highest and paid lowest (3 percent). So "email is as good as referral" holds for the first half-year and not beyond, which a single number would have hidden. This matches what we planted (paid customers' interest fades fastest; email's fades faster than referral's). The paid gap is large relative to the intervals, so we can state it with confidence (da.08); the email-organic difference at month 12 we cannot.

### 4.4 A simpler KPI: the 90-day repeat rate

Matrices are rich but hard to put on a dashboard. A single number such as the **90-day repeat rate** is a good KPI: the share of new customers who place a second order within 90 days. It must be computed only on customers observed long enough.

```python run
second = o.sort_values(["customer_id", "order_date"]).groupby("customer_id").nth(1)[["customer_id", "order_date"]].rename(columns={"order_date": "second_order"})
cu = customers.merge(second, on="customer_id", how="left", validate="1:1")
cu["days_to_second"] = (cu["second_order"] - cu["first_order"]).dt.days
eligible = cu[cu["first_order"] <= CUT - pd.Timedelta(days=90)].copy()                           # observed for at least 90 days
eligible["repeat90"] = eligible["days_to_second"].le(90).fillna(False)
t = eligible.groupby("channel")["repeat90"].agg(["sum", "size"])
t["rate %"] = t["sum"] / t["size"] * 100
ci = [wilson(r["sum"], r["size"]) for _, r in t.iterrows()]
t["CI low"], t["CI high"] = [c[0] * 100 for c in ci], [c[1] * 100 for c in ci]
print(t.round(1).to_string())
all_k, all_n = int(eligible["repeat90"].sum()), len(eligible)
print(f"all channels: {all_k / all_n * 100:.1f}% of {all_n:,} eligible customers (excluded: {len(cu) - all_n:,} acquired in the last 90 days)")
naive = cu["days_to_second"].le(90).fillna(False).mean() * 100
print(f"the naive rate that counts everyone: {naive:.1f}%  (too low, because it includes customers who have not had 90 days yet)")
```
```text
           sum  size  rate %  CI low  CI high
channel                                      
email      490   794   61.70   58.30    65.00
organic   1194  2182   54.70   52.60    56.80
paid       684  1875   36.50   34.30    38.70
referral   334   540   61.90   57.70    65.90
all channels: 50.1% of 5,391 eligible customers (excluded: 609 acquired in the last 90 days)
the naive rate that counts everyone: 48.6%  (too low, because it includes customers who have not had 90 days yet)
```

The eligibility rule matters: counting every customer (including the 609 acquired in the last 90 days) gives a lower rate (48.6 percent) than the correct one (50.1 percent), and the **error is largest exactly for the cohorts a manager looks at first**, the newest. About half of the customers place a second order within 90 days overall: email and referral at about 62 percent, organic at 55, and paid at 37.

> **Predict the output.** What is the 90-day repeat rate of the customers acquired in the **last** 90 days of the data, counting only the second orders that have happened so far? Higher or lower than the 50 percent of the eligible customers?

<details><summary>Answer</summary>

```python run
recent = cu[cu["first_order"] > CUT - pd.Timedelta(days=90)]
print("customers acquired in the last 90 days:", len(recent))
print("share with a second order so far:", round(recent["second_order"].notna().mean() * 100, 1), "% (the windows are incomplete, so this is a lower bound)")
last30 = cu[cu["first_order"] > CUT - pd.Timedelta(days=30)]
print("customers acquired in the last 30 days:", len(last30), "| share with a second order so far:", round(last30["second_order"].notna().mean() * 100, 1), "%")
```
```text
customers acquired in the last 90 days: 609
share with a second order so far: 35.6 % (the windows are incomplete, so this is a lower bound)
customers acquired in the last 30 days: 118 | share with a second order so far: 22.9 %
```

Lower: 36 percent against 50 for the customers acquired in the last 90 days, and 23 percent for those acquired in the last 30, because they have had only a few weeks, not 90 days, to place a second order. If a dashboard computed "the 90-day repeat rate of last month's customers", it would report a collapse that is only an artefact of the calendar. This is exactly why the eligibility rule exists.

</details>

### 4.5 Customer value: the LTV curve

How much is a customer worth? An **empirical LTV** adds up what customers actually spent, over a fixed horizon, among customers observed for the whole horizon. We use 12 months and the customers acquired in 2023 (all have a full year of follow-up by the end of 2024).

```python run
HORIZON = 365
oo = o.copy()
oo["days"] = (oo["order_date"] - oo["first_order"]).dt.days
full = customers[customers["first_order"] <= CUT - pd.Timedelta(days=HORIZON - 1)]               # observed for 365 days
rev12 = oo[(oo["days"] < HORIZON) & oo["customer_id"].isin(full["customer_id"])].groupby("customer_id")["amount"].sum()
full = full.assign(rev12=rev12.reindex(full["customer_id"]).fillna(0).to_numpy())
print("customers with a full year of follow-up:", len(full), "of", len(customers))
res = []
for ch, g in full.groupby("channel"):
    m = g["rev12"].mean()
    se = g["rev12"].std(ddof=1) / np.sqrt(len(g))
    res.append({"channel": ch, "customers": len(g), "12-month revenue per customer": m, "CI low": m - 1.96 * se, "CI high": m + 1.96 * se, "orders per customer": round(float(oo[(oo["days"] < HORIZON) & oo["customer_id"].isin(g["customer_id"])].groupby("customer_id").size().reindex(g["customer_id"]).fillna(0).mean()), 2)})
ltv = pd.DataFrame(res).set_index("channel")
print(ltv.round({"12-month revenue per customer": 0, "CI low": 0, "CI high": 0, "orders per customer": 2}).to_string())
print(f"\nall channels: {full['rev12'].mean():,.0f} rupees per customer in the first 12 months")
```
```text
customers with a full year of follow-up: 2992 of 6000
          customers  12-month revenue per customer   CI low  CI high  orders per customer
channel                                                                                  
email           465                       3,550.00 3,287.00 3,812.00                 4.45
organic        1191                       2,941.00 2,799.00 3,083.00                 3.53
paid           1030                       1,819.00 1,733.00 1,906.00                 2.20
referral        306                       4,141.00 3,760.00 4,522.00                 5.04

all channels: 2,772 rupees per customer in the first 12 months
```

Referral and email customers bring about twice the 12-month revenue of paid customers (4,141 and 3,550 against 1,819), and the intervals do not overlap. That is **revenue**; to decide where to spend acquisition money you need **contribution** (after the cost of goods) set against the **cost to acquire** them (CAC). The marketing team provides the CAC of each channel (an assumption); the contribution margin is the 30 percent of section 2.

```python run
CAC = {"organic": 150, "paid": 420, "email": 80, "referral": 200}          # assumptions from marketing (rupees per acquired customer)
ltv["contribution"] = ltv["12-month revenue per customer"] * MARGIN
ltv["contribution CI low"], ltv["contribution CI high"] = ltv["CI low"] * MARGIN, ltv["CI high"] * MARGIN
ltv["CAC"] = pd.Series(CAC)
ltv["LTV12 / CAC"] = ltv["contribution"] / ltv["CAC"]
ltv["ratio CI low"], ltv["ratio CI high"] = ltv["contribution CI low"] / ltv["CAC"], ltv["contribution CI high"] / ltv["CAC"]
print(ltv[["contribution", "CAC", "LTV12 / CAC", "ratio CI low", "ratio CI high"]].round(2).to_string())
```
```text
          contribution  CAC  LTV12 / CAC  ratio CI low  ratio CI high
channel                                                              
email         1,064.87   80        13.31         12.33          14.30
organic         882.21  150         5.88          5.60           6.17
paid            545.82  420         1.30          1.24           1.36
referral      1,242.26  200         6.21          5.64           6.78
```

A common rule of thumb says LTV/CAC should be at least 3. By the 12-month measure, **email** is outstanding (13), organic and referral are healthy (about 6), and **paid advertising is weak** (1.3, with an interval from 1.2 to 1.4): each paid customer earns back a little more than it cost in the first year, far below the usual standard. That does not mean "stop paid": there may be a payoff after month 12, and paid customers may bring other value (volume, brand awareness). It means the paid budget should be defended with a longer-horizon argument, not with the 12-month numbers, and the channel is the first place to look for savings. Note the assumptions: the margin (30 percent) and the CACs are given by other teams and carry their own uncertainty, which the intervals above do not include.

A **payback curve** shows when each channel recovers its acquisition cost:

```python run
cum = {}
for ch, g in full.groupby("channel"):
    sub = oo[oo["customer_id"].isin(g["customer_id"]) & (oo["days"] < HORIZON)].copy()
    sub["m"] = (sub["days"] // 30.44).astype(int).clip(upper=11)
    c = sub.groupby("m")["amount"].sum().reindex(range(12), fill_value=0).cumsum() / len(g) * MARGIN
    cum[ch] = c
pay = pd.DataFrame(cum)
pay.index = [f"M{m}" for m in pay.index]
print(pay.round(0).loc[["M0", "M1", "M2", "M3", "M6", "M9", "M11"]].to_string())
payback = {ch: next((i for i, v in enumerate(pay[ch]) if v >= CAC[ch]), None) for ch in pay.columns}
print("\nmonth in which cumulative contribution first reaches the CAC:", {k: (f"M{v}" if v is not None else "not within 12 months") for k, v in payback.items()})
```
```text
       email  organic   paid  referral
M0    346.00   335.00 301.00    352.00
M1    438.00   416.00 342.00    469.00
M2    539.00   487.00 378.00    569.00
M3    621.00   551.00 406.00    679.00
M6    819.00   706.00 481.00    929.00
M9    983.00   820.00 527.00  1,136.00
M11 1,065.00   882.00 546.00  1,242.00

month in which cumulative contribution first reaches the CAC: {'email': 'M0', 'organic': 'M0', 'paid': 'M4', 'referral': 'M0'}
```

Email, organic and referral recover their acquisition cost on the **first order** (month 0); **paid takes about four months** (its first order contributes less than its CAC, and these customers reorder least). This is the answer to the business question for Q3 in business terms, and each row carries uncertainty that the next section's recommendation must state.

### 4.6 Retention without a table: time to the second order

For a customer who buys once, how long until they buy again, and how many never do? The **time to second order** is a survival-type question; the complication is again immaturity: a customer observed for 60 days who has not reordered has not "never reordered", only "not yet". Using only customers observed for at least a year makes the share clean.

```python run
yr = cu[cu["first_order"] <= CUT - pd.Timedelta(days=365)].copy()
yr["reorders_in_year"] = yr["days_to_second"].le(365).fillna(False)
t = yr.groupby("channel")["reorders_in_year"].agg(["sum", "size"])
t["one-time buyers %"] = (1 - t["sum"] / t["size"]) * 100
print(t[["size", "one-time buyers %"]].round(1).to_string())
d = yr.loc[yr["days_to_second"].le(365), "days_to_second"]
print(f"\namong customers who reorder within a year: median {d.median():.0f} days to the second order, 75% within {d.quantile(.75):.0f} days")
```
```text
          size  one-time buyers %
channel                          
email      464              15.10
organic   1189              18.30
paid      1026              38.10
referral   305              12.50

among customers who reorder within a year: median 52 days to the second order, 75% within 117 days
```

Between 13 and 38 percent of customers (depending on the channel) never place a second order within a year, and those who do mostly do it within four months (the median is 52 days; three quarters within 117). Two practical messages follow: the **first 90 days** decide most of the retention (so the "second order" campaigns belong there), and a **one-time buyer** is the largest single segment, which is the starting point of the segmentation in section 5.

### 4.7 Cohort quality over time

Retention matrices let you ask whether recent cohorts are better or worse than old ones (is acquisition quality changing?). Compare the 3-month retention of each quarter's acquisitions:

```python run
cu2 = customers.assign(cohort=customers["first_order"].dt.to_period("Q"))
rows = []
for q, g in cu2.groupby("cohort"):
    if q.end_time.to_period("M") + 3 > LAST:
        continue                                                              # the 3-month window is not complete for the latest quarter
    ids = set(g["customer_id"])
    act = o[(o["k"] == 3) & o["customer_id"].isin(ids)]["customer_id"].nunique()
    lo, hi = wilson(act, len(g))
    rows.append({"quarter": str(q), "customers": len(g), "M3 retention %": act / len(g) * 100, "CI low": lo * 100, "CI high": hi * 100})
print(pd.DataFrame(rows).round(1).to_string(index=False))
```
```text
quarter  customers  M3 retention %  CI low  CI high
 2023Q1        698           20.90   18.10    24.10
 2023Q2        723           22.10   19.30    25.30
 2023Q3        763           20.80   18.10    23.90
 2023Q4        794           20.00   17.40    23.00
 2024Q1        795           19.50   16.90    22.40
 2024Q2        803           21.30   18.60    24.30
 2024Q3        790           19.70   17.10    22.70
```

The quarterly values are flat within their intervals: no sign that acquisition quality is getting better or worse. If it were drifting, the first question would be whether the *channel mix* changed (da.10's mix decomposition) before concluding that customers got worse. A flat line is also a result: "stable" is worth reporting.


## 5. RFM segmentation

### 5.1 The question

*Who are our best customers, who is slipping away, and what should marketing do for each group?* A shop with 6,000 customers cannot treat them all the same, and cannot design 6,000 treatments. **Segmentation** puts customers into a few groups that behave differently enough to deserve different actions. **RFM** is the classic, simple and surprisingly effective way to do it from order history alone. Each customer is described by three numbers.

| Letter | Measure | Definition (as of a date) | Reading |
|---|---|---|---|
| **R** Recency | days since the last order | as-of date minus the date of the latest order | small = recently active |
| **F** Frequency | number of orders | count of orders up to the as-of date | large = habitual |
| **M** Monetary | total spend | sum of order amounts up to the as-of date | large = valuable |

Everything in RFM depends on the **as-of date**: recompute it as time passes, and say which date a table refers to.

```python run
ASOF = pd.Timestamp("2024-12-31")


def rfm_table(orders, customers, asof):
    od = orders[orders["order_date"] <= asof]
    g = od.groupby("customer_id").agg(last_order=("order_date", "max"), F=("amount", "size"), M=("amount", "sum"))
    g["R"] = (asof - g["last_order"]).dt.days
    out = customers.set_index("customer_id")[["first_order", "channel"]].join(g[["R", "F", "M"]], how="inner")
    return out


rfm = rfm_table(orders, customers, ASOF)
print(rfm.shape, "| grain: one row per customer who had ordered by the as-of date")
print(rfm[["R", "F", "M"]].describe(percentiles=[.25, .5, .75, .9]).round(0).to_string())
```
```text
(6000, 5) | grain: one row per customer who had ordered by the as-of date
             R        F         M
count 6,000.00 6,000.00  6,000.00
mean    214.00     3.00  2,570.00
std     183.00     3.00  2,496.00
min       1.00     1.00     96.00
25%      64.00     1.00    961.00
50%     158.00     2.00  1,768.00
75%     326.00     4.00  3,263.00
90%     503.00     6.00  5,482.00
max     730.00    25.00 29,745.00
```

All three are right-skewed (the mean is above the median; the maximum is far above the 90th percentile), as money and counts usually are. Half of the customers placed two orders or fewer, and the top 10 percent have six or more.

### 5.2 Turning measures into scores

Raw numbers are on different scales, so each is turned into a **score from 1 to 5** (5 is best) by cutting it at quintiles. The pandas tool is `qcut`, and it fails on the data we have:

```python run
try:
    pd.qcut(rfm["F"], 5, labels=[1, 2, 3, 4, 5])
except ValueError as e:
    print("ValueError:", str(e)[:90])
print("share of customers with exactly one order:", round((rfm["F"] == 1).mean() * 100, 1), "%")
print("share with one or two orders             :", round((rfm["F"] <= 2).mean() * 100, 1), "%")
```
```text
ValueError: Bin edges must be unique: Index([1.0, 1.0, 2.0, 3.0, 5.0, 25.0], dtype='float64', name='F'
share of customers with exactly one order: 30.6 %
share with one or two orders             : 54.0 %
```

`qcut` needs five bins with distinct edges, but almost a third of the customers share the value `F = 1`, so the first edges coincide. A common workaround is to rank the values first (`rank(method="first")`), which breaks ties by row order, but that gives customers with **the same behaviour** different scores purely by chance:

```python run
f_rank = pd.qcut(rfm["F"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
one_order = rfm["F"] == 1
print("customers with F = 1 get these scores under rank-first:", f_rank[one_order].value_counts().sort_index().to_dict())
```
```text
customers with F = 1 get these scores under rank-first: {1: 1200, 2: 639}
```

Identical customers (one order each) receive scores 1 and 2 depending on an arbitrary tie-break: that is a false distinction. For a variable with big ties, **define the bins by hand** from the business meaning (one order, two, three, four to five, six or more). For continuous variables such as spend and recency, quantiles are fine.

```python run
def score_quantile(s, higher_is_better=True, n=5):
    r = s.rank(method="first", ascending=higher_is_better)
    return pd.qcut(r, n, labels=list(range(1, n + 1))).astype(int)


rfm["R_score"] = score_quantile(rfm["R"], higher_is_better=False)                    # a SMALL recency (recent) gets score 5
rfm["F_score"] = pd.cut(rfm["F"], [0, 1, 2, 3, 5, np.inf], labels=[1, 2, 3, 4, 5]).astype(int)   # hand-made bins for a heavily tied variable
rfm["M_score"] = score_quantile(rfm["M"], higher_is_better=True)
print(rfm.groupby("F_score")["F"].agg(["min", "max", "size"]).to_string())
print()
print(rfm.groupby("R_score")["R"].agg(["min", "max", "size"]).to_string())
print()
print(rfm.groupby("M_score")["M"].agg(["min", "max", "size"]).round(0).to_string())
```
```text
         min  max  size
F_score                
1          1    1  1839
2          2    2  1401
3          3    3   923
4          4    5   999
5          6   25   838

         min  max  size
R_score                
1        375  730  1200
2        214  375  1200
3        113  214  1200
4         49  113  1200
5          1   49  1200

             min       max  size
M_score                         
1          96.00    833.00  1200
2         834.00  1,406.00  1200
3       1,406.00  2,258.00  1200
4       2,259.00  3,739.00  1200
5       3,741.00 29,745.00  1200
```

The tables are the **audit** of the scoring: each score has a clear range, the F bins do not split identical customers, and the R and M scores have equal sizes (quantiles). Whenever a score is built by a cut, print its ranges.

### 5.3 From scores to segments

Scores are not segments. A segment has a **meaning** and a **name** that a marketer understands. A usual rule set uses recency and frequency (the two most informative):

| Segment | Rule | What it means |
|---|---|---|
| **Champions** | R >= 4 and F >= 4 | bought recently, often |
| **Loyal** | R >= 3 and F >= 3 (and not a champion) | regulars, fairly recent |
| **New / promising** | R >= 4 and F <= 2 | recent, few orders so far |
| **At risk** | R <= 2 and F >= 3 | used to buy often, gone quiet |
| **Hibernating** | R <= 2 and F <= 2 | one or two orders, long ago |
| **Needs attention** | everything else | in between |

```python run
def segment(r, f):
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / promising"
    if r <= 2 and f >= 3:
        return "At risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    return "Needs attention"


rfm["segment"] = [segment(r, f) for r, f in zip(rfm["R_score"], rfm["F_score"])]
order = ["Champions", "Loyal", "New / promising", "Needs attention", "At risk", "Hibernating"]
prof = rfm.groupby("segment").agg(customers=("R", "size"), R=("R", "mean"), F=("F", "mean"), M=("M", "mean"), revenue=("M", "sum")).loc[order]
prof["% of customers"] = prof["customers"] / len(rfm) * 100
prof["% of revenue"] = prof["revenue"] / prof["revenue"].sum() * 100
print(prof.round(1).to_string())
print("\nsegments cover everyone exactly once:", int(prof["customers"].sum()) == len(rfm))
```
```text
                 customers      R    F        M      revenue  % of customers  % of revenue
segment                                                                                   
Champions             1004  49.50 6.60 5,454.30 5,476,093.00           16.70         35.50
Loyal                  976 113.10 4.20 3,451.10 3,368,254.00           16.30         21.80
New / promising        998  54.70 1.50 1,256.20 1,253,683.00           16.60          8.10
Needs attention        622 163.20 1.50 1,217.90   757,524.00           10.40          4.90
At risk                780 349.70 4.30 3,479.60 2,714,112.00           13.00         17.60
Hibernating           1620 428.70 1.40 1,141.20 1,848,752.00           27.00         12.00

segments cover everyone exactly once: True
```

Read the profile like an analyst. **Champions** are 17 percent of the customers and bring 36 percent of the revenue. **Hibernating** customers (one or two orders, a long time ago) are the largest single group by headcount (27 percent) but bring only 12 percent of the revenue. **At risk** customers (13 percent of customers, 18 percent of revenue) have a high past value and low recency: the most valuable group to win back. The rule set is a choice: another team might draw the lines elsewhere. What matters is that the segments are **mutually exclusive and exhaustive** (the last line checks it) and that they differ.

```python run
cum = prof["revenue"].sort_values(ascending=False).cumsum() / prof["revenue"].sum() * 100
top_customers = rfm["M"].sort_values(ascending=False)
share_top20 = top_customers.head(int(len(rfm) * .2)).sum() / top_customers.sum() * 100
print(f"the top 20% of customers by spend bring {share_top20:.0f}% of lifetime revenue (a Pareto pattern, weaker than the 80/20 myth)")
chan_mix = pd.crosstab(rfm["segment"], rfm["channel"], normalize="index").loc[order] * 100
print(chan_mix.round(0).to_string())
```
```text
the top 20% of customers by spend bring 50% of lifetime revenue (a Pareto pattern, weaker than the 80/20 myth)
channel          email  organic  paid  referral
segment                                        
Champions        24.00    47.00 10.00     20.00
Loyal            19.00    47.00 22.00     12.00
New / promising  14.00    39.00 37.00     10.00
Needs attention   9.00    40.00 44.00      7.00
At risk          16.00    43.00 33.00      8.00
Hibernating       9.00    32.00 54.00      5.00
```

The channel mix by segment shows what we found in section 4: referral and email customers are over-represented among Champions and Loyal, paid customers among Hibernating. Segmentation and channel analysis tell the same story from two sides.

### 5.4 Do the segments mean anything? Test on the future

A segmentation can look sensible and be useless. The real test is **predictive**: do the segments differ in what customers do *next*? Build RFM as of an earlier date, then look at spending in the period that followed, which the segmentation did not see.

```python run
T = pd.Timestamp("2024-06-30")
rfm_T = rfm_table(orders, customers, T)
rfm_T["R_score"] = score_quantile(rfm_T["R"], higher_is_better=False)
rfm_T["F_score"] = pd.cut(rfm_T["F"], [0, 1, 2, 3, 5, np.inf], labels=[1, 2, 3, 4, 5]).astype(int)
rfm_T["M_score"] = score_quantile(rfm_T["M"], higher_is_better=True)
rfm_T["segment"] = [segment(r, f) for r, f in zip(rfm_T["R_score"], rfm_T["F_score"])]
future = orders[(orders["order_date"] > T) & (orders["order_date"] <= ASOF)].groupby("customer_id")["amount"].agg(future_orders="size", future_spend="sum")
rfm_T = rfm_T.join(future).fillna({"future_orders": 0, "future_spend": 0})
rows = []
for seg in order:
    g = rfm_T[rfm_T["segment"] == seg]
    m, se = g["future_spend"].mean(), g["future_spend"].std(ddof=1) / np.sqrt(len(g))
    rows.append({"segment": seg, "customers": len(g), "bought again %": (g["future_orders"] > 0).mean() * 100,
                 "future spend per customer": m, "CI low": m - 1.96 * se, "CI high": m + 1.96 * se})
vt = pd.DataFrame(rows).set_index("segment")
print(f"segments built as of {T.date()}; outcome = spend in the following 6 months")
print(vt.round(1).to_string())
print(f"\nall customers: {rfm_T['future_spend'].mean():,.0f} per customer; {(rfm_T['future_orders'] > 0).mean() * 100:.0f}% bought again")
```
```text
segments built as of 2024-06-30; outcome = spend in the following 6 months
                 customers  bought again %  future spend per customer   CI low  CI high
segment                                                                                
Champions              628           64.80                   1,133.90 1,025.60 1,242.10
Loyal                  717           52.00                     751.90   665.80   838.10
New / promising        915           51.80                     888.70   793.20   984.30
Needs attention        485           41.00                     531.40   450.80   612.10
At risk                504           31.50                     342.80   287.40   398.20
Hibernating           1327           18.50                     195.00   166.60   223.50

all customers: 602 per customer; 41% bought again
```

This is the table that justifies the whole exercise. Champions spent 1,134 rupees per customer in the following six months, nearly twice the average (602), and hibernating customers spent 195, about a third of it; the intervals separate the top and bottom segments clearly, and the order of the six segments by future spend is nearly the planned one (the only swap is Loyal and New / promising, whose intervals overlap). The segments predict **future behaviour**, not only past behaviour, so they are useful for targeting. If the future-spend column were flat, the segmentation would be a pretty picture.

One more view of predictive power, the **gains curve**: sort customers by their RFM total score and see what share of the *future* revenue the top 10, 20, 30 percent of customers capture.

```python run
rfm_T["score"] = rfm_T["R_score"] + rfm_T["F_score"] + rfm_T["M_score"] + rfm_T["R_score"] * 0.001      # a small tie-breaker for recency
ranked = rfm_T.sort_values("score", ascending=False)["future_spend"]
tot = ranked.sum()
rand = rfm_T["future_spend"].sample(frac=1, random_state=0)
print("share of FUTURE revenue captured by the top x% of customers (ranked by RFM at the earlier date)")
for pct in (10, 20, 30, 50):
    k = int(len(ranked) * pct / 100)
    print(f"  top {pct:2d}%: RFM captures {ranked.head(k).sum() / tot * 100:4.0f}% | a random pick would capture {rand.head(k).sum() / tot * 100:4.0f}%")
```
```text
share of FUTURE revenue captured by the top x% of customers (ranked by RFM at the earlier date)
  top 10%: RFM captures   21% | a random pick would capture   10%
  top 20%: RFM captures   38% | a random pick would capture   20%
  top 30%: RFM captures   51% | a random pick would capture   29%
  top 50%: RFM captures   72% | a random pick would capture   52%
```

The top 20 percent by RFM captures 38 percent of the revenue of the next six months, against 20 percent for a random choice: a **lift** of about 1.9 for marketing that can only target a fifth of the base (and 51 percent of future revenue from the top 30 percent). That is a number a marketing manager understands.

### 5.5 A data-driven alternative: k-means

The rule-based segments depend on thresholds someone chose. **Clustering** lets the data propose groups. **k-means** puts customers into `k` groups so that customers in a group are close in (standardised) R, F and M. Because the variables are skewed, we first take logarithms; because they have different scales, we standardise.

```python run
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler

Xr = StandardScaler().fit_transform(np.log1p(rfm[["R", "F", "M"]]))
sil = {}
for k in (3, 4, 5, 6, 7):
    km = KMeans(n_clusters=k, n_init=5, random_state=0).fit(Xr)
    sil[k] = silhouette_score(Xr, km.labels_, sample_size=3000, random_state=0)
print("silhouette score by number of clusters (higher is better separation):", {k: round(v, 3) for k, v in sil.items()})
```
```text
silhouette score by number of clusters (higher is better separation): {3: 0.368, 4: 0.348, 5: 0.334, 6: 0.316, 7: 0.322}
```

The **silhouette score** measures how well separated the clusters are (between -1 and 1). The scores are low and fall only slowly from 3 to 7 clusters (0.37 to 0.32): customer behaviour is continuous, not made of clean blobs, so there is no sharp winner, and the number of clusters is partly a business choice. We take 5, a size marketing can manage, and describe the clusters.

```python run
km = KMeans(n_clusters=5, n_init=10, random_state=0).fit(Xr)
rfm["cluster"] = km.labels_
cprof = rfm.groupby("cluster").agg(customers=("R", "size"), R=("R", "median"), F=("F", "median"), M=("M", "median"), revenue=("M", "sum"))
cprof["% of revenue"] = cprof["revenue"] / cprof["revenue"].sum() * 100
print(cprof.sort_values("M", ascending=False).round(0).to_string())
print("\nhow the clusters map to the rule-based segments (row % of each cluster):")
print((pd.crosstab(rfm["cluster"], rfm["segment"], normalize="index")[order] * 100).round(0).to_string())
```
```text
         customers      R    F        M      revenue  % of revenue
cluster                                                           
3              912  90.00 7.00 5,956.00 6,156,420.00         40.00
1              757  19.00 3.00 2,636.00 2,290,817.00         15.00
4             1839 228.00 3.00 2,368.00 4,699,544.00         30.00
2              949  69.00 1.00   957.00   954,808.00          6.00
0             1543 375.00 1.00   806.00 1,316,829.00          9.00

how the clusters map to the rule-based segments (row % of each cluster):
segment  Champions  Loyal  New / promising  Needs attention  At risk  Hibernating
cluster                                                                          
0             0.00   0.00             0.00            18.00     0.00        82.00
1            46.00  31.00            23.00             0.00     0.00         0.00
2             0.00   2.00            81.00            17.00     0.00         0.00
3            61.00  23.00             0.00             0.00    15.00         0.00
4             5.00  28.00             3.00            10.00    35.00        19.00
```

The clusters broadly rediscover the rule-based segments (a high-value, high-frequency, recent cluster; a large cluster of one-time old customers; and groups in between), which is reassuring: two different methods agree on the main structure. They also disagree at the edges, as expected.

Clustering needs one more check, **stability**: if you run it again with a different starting point or a subsample, do you get the same groups? Unstable clusters are noise.

```python run
labels = []
for seed in range(6):
    labels.append(KMeans(n_clusters=5, n_init=1, random_state=seed).fit(Xr).labels_)
aris = [adjusted_rand_score(labels[i], labels[j]) for i in range(6) for j in range(i + 1, 6)]
print(f"agreement between 6 runs with different starts (adjusted Rand index, 1 = identical): min {min(aris):.2f}, mean {np.mean(aris):.2f}")
rng = np.random.default_rng(1)
idx = rng.choice(len(Xr), int(len(Xr) * .8), replace=False)
km_sub = KMeans(n_clusters=5, n_init=10, random_state=0).fit(Xr[idx])
print(f"agreement between the full fit and a fit on 80% of customers: {adjusted_rand_score(km.labels_[idx], km_sub.predict(Xr[idx])):.2f}")
```
```text
agreement between 6 runs with different starts (adjusted Rand index, 1 = identical): min 0.42, mean 0.68
agreement between the full fit and a fit on 80% of customers: 0.93
```

The results are mixed, which is typical. Different starting points (with a single initialisation each) agree with each other at an average adjusted Rand index of 0.68, with a worst pair at 0.42: some starts find a different solution. The fit on 80 percent of the customers, with several initialisations, agrees with the full fit at 0.93. The practical rules: always use several initialisations (`n_init` of 10 or more), check the stability before you name the clusters, and treat the boundaries as fuzzy. The practical advice: use **rule-based RFM** when you need simple, explainable segments that a marketer can recompute and monitor; use **k-means** to explore and to check that your rules are sensible; always validate against the future, as in 5.4.

### 5.6 From segments to actions

A segment is useful only if it triggers a **different action** and the action has an expected payoff. For each segment, write what the customers are doing, the action, how to measure it, and the size of the prize, with its uncertainty. The last column of a good table is "how we will test it", because response rates are assumptions until measured (section 2).

```python run
aov_all = orders["amount"].mean()
at_risk = prof.loc["At risk"]
hib = prof.loc["Hibernating"]
plans = pd.DataFrame([
    ("Champions", int(prof.loc["Champions", "customers"]), "protect: early access, no discounts (they buy anyway)", "retention of this group", "A/B: early-access offer vs nothing"),
    ("Loyal", int(prof.loc["Loyal", "customers"]), "grow frequency: bundles, loyalty points", "orders per customer", "A/B: points programme"),
    ("New / promising", int(prof.loc["New / promising", "customers"]), "second-order push within 30 days", "90-day repeat rate", "A/B: email on day 10 vs none"),
    ("At risk", int(at_risk["customers"]), "win-back offer; they bought often before", "reactivation rate, revenue", "A/B: offer vs control"),
    ("Hibernating", int(hib["customers"]), "low-cost email only; do not spend on discounts", "reactivation rate at low cost", "holdout group"),
], columns=["segment", "customers", "action", "metric", "how to test"])
print(plans.to_string(index=False))
```
```text
        segment  customers                                                action                        metric                        how to test
      Champions       1004 protect: early access, no discounts (they buy anyway)       retention of this group A/B: early-access offer vs nothing
          Loyal        976               grow frequency: bundles, loyalty points           orders per customer              A/B: points programme
New / promising        998                      second-order push within 30 days            90-day repeat rate       A/B: email on day 10 vs none
        At risk        780              win-back offer; they bought often before    reactivation rate, revenue              A/B: offer vs control
    Hibernating       1620        low-cost email only; do not spend on discounts reactivation rate at low cost                      holdout group
```

A rough size of the prize for the most promising action, **win-back of the at-risk group**, using explicit assumptions for the response rate (unknown until tested) and the order value:

```python run
n_risk = int(at_risk["customers"])
print(f"at-risk customers: {n_risk:,} | average order value {aov_all:,.0f} | their lifetime spend so far: {at_risk['M']:,.0f} per customer")
print("assumed reactivation rate -> extra orders and revenue (one order each, before any offer cost):")
for rate in (0.03, 0.06, 0.10):
    print(f"  {rate * 100:4.0f}%: {n_risk * rate:6.0f} customers reactivated, about {n_risk * rate * aov_all:,.0f} rupees")
```
```text
at-risk customers: 780 | average order value 823 | their lifetime spend so far: 3,480 per customer
assumed reactivation rate -> extra orders and revenue (one order each, before any offer cost):
     3%:     23 customers reactivated, about 19,252 rupees
     6%:     47 customers reactivated, about 38,505 rupees
    10%:     78 customers reactivated, about 64,175 rupees
```

The honest framing is the range: a win-back campaign that reactivates 3 to 10 percent of the 780 at-risk customers brings 23 to 78 orders, worth about 19,000 to 64,000 rupees for one order each (more if the reactivated customers keep buying), minus the cost of the offer. That is a **small prize** for a group this size, which is itself a finding: a campaign should cost well under 19,000 rupees to be worth running. The reactivation rate is **an assumption**, and the experiment of section 2 is how to turn it into a measurement (and, with only 780 customers, a test would be badly underpowered for a reactivation difference of a few percentage points, and the sample size calculation of section 2 says so before any money is spent).

### 5.7 RFM pitfalls

| Pitfall | What goes wrong | What to do |
|---|---|---|
| Forgetting the **as-of date** | a table nobody can reproduce | store the date; recompute on a schedule |
| `qcut` with heavy ties | error, or arbitrary splitting of identical customers | hand-made bins for tied variables |
| Quantile scores | segment sizes are fixed by construction (20 percent per score), so "20 percent are Champions" says nothing | judge segments by behaviour, not by size |
| Tenure confounding | new customers cannot have a high F | add tenure, or look at rates per month of tenure |
| One-time buyers dominate | the base is mostly segment "Hibernating" | treat acquisition and repeat separately (section 4) |
| Not validated on the future | pretty segments, no predictive value | holdout test as in 5.4 |
| Unstable clusters | different runs, different groups | stability check; prefer simple rules for operations |
| Reading RFM as causal | "champions buy because of our emails" | RFM describes; experiments decide |
| Seasonality | recency is distorted at the holiday peak | compare like periods; document the date |


## 6. From analyses to a recommendation

### 6.1 Four answers on one page

Each analysis gave an answer with a size and a range. A manager cannot hold four separate reports in their head; the synthesis is a single table, filled from the numbers computed above, in business units.

```python run
net_value = lambda c, cac: c - cac                                              # 12-month contribution minus the cost of acquiring the customer
ltv["net_12m"] = ltv["contribution"] - ltv["CAC"]
ltv["net_lo"] = ltv["contribution CI low"] - ltv["CAC"]
ltv["net_hi"] = ltv["contribution CI high"] - ltv["CAC"]
gap_share = (0.3, 1.0)                                                          # assume a redesign closes 30% to 100% of the mobile checkout gap
mob_lo, mob_hi = (OPP["mid"] * g * OPP["aov"] * MARGIN for g in gap_share)
syn = pd.DataFrame([
    ("Q1  free-shipping banner", f"conversion {AB['conv_diff_pts']:+.2f} points (CI {AB['conv_lo']:+.2f} to {AB['conv_hi']:+.2f}, p = {AB['conv_p']:.2f})",
     f"net contribution {AB['net_mid'] / 1000:+.0f}k a month (range {AB['net_lo'] / 1000:+.0f}k to {AB['net_hi'] / 1000:+.0f}k)", "inconclusive; does not clearly pay"),
    ("Q2  funnel", f"mobile cart-to-checkout {OPP['now_rate'] * 100:.0f}% against {OPP['desk_rate'] * 100:.0f}% on desktop, in every channel",
     f"{OPP['mid'] * gap_share[0]:,.0f} to {OPP['mid'] * gap_share[1]:,.0f} extra orders a month; {mob_lo / 1000:,.0f}k to {mob_hi / 1000:,.0f}k contribution", "gap is certain; size of a fix is an assumption"),
    ("Q3  channels and value", f"12-month LTV / CAC: email {ltv.loc['email', 'LTV12 / CAC']:.0f}, referral {ltv.loc['referral', 'LTV12 / CAC']:.0f}, organic {ltv.loc['organic', 'LTV12 / CAC']:.0f}, paid {ltv.loc['paid', 'LTV12 / CAC']:.1f}",
     f"net 12-month value per customer: paid {ltv.loc['paid', 'net_12m']:,.0f}, organic {ltv.loc['organic', 'net_12m']:,.0f}, referral {ltv.loc['referral', 'net_12m']:,.0f}", "high; margin and CAC are assumptions"),
    ("Q4  RFM segments", f"top segment ({prof.loc['Champions', 'customers']:,.0f} customers) spends {vt.loc['Champions', 'future spend per customer'] / rfm_T['future_spend'].mean():.1f}x the average next half-year; the bottom {vt.loc['Hibernating', 'future spend per customer'] / rfm_T['future_spend'].mean():.1f}x",
     "win-back of the at-risk segment: 19k to 64k rupees of revenue (small)", "segments are predictive; payoff small"),
], columns=["question", "finding", "size (with range)", "confidence"])
pd.set_option("display.max_colwidth", 70)
print(syn.to_string(index=False))
```
```text
                question                                                                               finding                                                      size (with range)                                     confidence
Q1  free-shipping banner                                 conversion +0.35 points (CI -0.28 to +0.98, p = 0.27)                   net contribution -16k a month (range -140k to +109k)             inconclusive; does not clearly pay
              Q2  funnel                  mobile cart-to-checkout 45% against 65% on desktop, in every channel            332 to 1,107 extra orders a month; 86k to 286k contribution gap is certain; size of a fix is an assumption
  Q3  channels and value                         12-month LTV / CAC: email 13, referral 6, organic 6, paid 1.3 net 12-month value per customer: paid 126, organic 732, referral 1,042           high; margin and CAC are assumptions
        Q4  RFM segments top segment (1,004 customers) spends 1.9x the average next half-year; the bottom 0.3x  win-back of the at-risk segment: 19k to 64k rupees of revenue (small)          segments are predictive; payoff small
```

Notice how each answer is stated in the form the manager needs: the finding with its interval, the size in rupees or orders as a **range**, and the confidence. The four answers differ in kind. Q2 has a certain *diagnosis* and an uncertain *prize*; Q1 has a precise result that does not support a decision; Q3 is a strong comparison resting on assumptions that others own; Q4 is a good description with a small payoff. A reader should see these differences, not a list of four equally confident bullets.

### 6.2 Prioritise: impact, confidence, effort

Resources are limited, so the recommendation is an **ordering**. A simple way: for each candidate, write the impact as a range, rate your confidence, add the effort (from the teams that would do it: here an assumption), and sort by expected payoff per unit of effort, keeping the uncertainty visible.

```python run
paid_net, org_net = ltv.loc["paid", "net_12m"], ltv.loc["organic", "net_12m"]
cands = pd.DataFrame([
    ("Fix the mobile checkout", mob_lo / 1000, mob_hi / 1000, "medium", "M", "design and run an A/B test of the redesign; the funnel gives the minimum effect to power it"),
    ("Cut or reshape paid-ad spend (per 100 customers moved, 12 months)", 100 * (org_net - paid_net) / 1000, 100 * (ltv.loc["referral", "net_12m"] - paid_net) / 1000, "high (the gap is large)", "S", f"each paid customer nets {paid_net:,.0f} in 12 months against {org_net:,.0f} for organic; shift budget to email and referral (limited capacity) or lower CAC"),
    ("Free-shipping banner for everyone", AB["net_lo"] / 1000, AB["net_hi"] / 1000, "low", "S", "do not roll out; test a basket-threshold version"),
    ("Win-back offer for the at-risk segment", 19 * MARGIN, 64 * MARGIN, "medium", "S", "test small; offer cost must stay far below the prize"),
], columns=["candidate", "contribution low (k/month)", "contribution high (k/month)", "confidence", "effort", "next step"])
print(cands.round(0).to_string(index=False))
print("\n(paid row: contribution per 100 customers moved from paid to organic or referral, over 12 months; moving them is limited by capacity)")
```
```text
                                                        candidate  contribution low (k/month)  contribution high (k/month)              confidence effort                                                                                                                            next step
                                          Fix the mobile checkout                       86.00                       286.00                  medium      M                                          design and run an A/B test of the redesign; the funnel gives the minimum effect to power it
Cut or reshape paid-ad spend (per 100 customers moved, 12 months)                       61.00                        92.00 high (the gap is large)      S each paid customer nets 126 in 12 months against 732 for organic; shift budget to email and referral (limited capacity) or lower CAC
                                Free-shipping banner for everyone                     -140.00                       109.00                     low      S                                                                                     do not roll out; test a basket-threshold version
                           Win-back offer for the at-risk segment                        6.00                        19.00                  medium      S                                                                                 test small; offer cost must stay far below the prize

(paid row: contribution per 100 customers moved from paid to organic or referral, over 12 months; moving them is limited by capacity)
```

The ordering that follows from the table is not a formula but an argument: the **mobile checkout** has the largest, best-grounded prize (the gap is certain; the fix's effect must be tested); **paid acquisition** is the cheapest lever and the evidence is strong (the comparison is large and the intervals do not overlap), but the capacity of the better channels is limited (you cannot buy more "referral" customers on demand), so a cut is safer than a reallocation; the **banner** should not be rolled out on this evidence; the **win-back** is a small prize and is only worth running if it is almost free. Writing the argument is more useful than any score.

### 6.3 What we do not know

Every analysis rests on assumptions, and the recommendation must list the ones that could change it. Here they are, in order of how much they matter.

| Limitation | Which answer it affects | Why it matters |
|---|---|---|
| The A/B test was **underpowered**: only about a third of the 37,000 visitors per group needed for the 0.5-point threshold | Q1 | "not significant" is not "no effect" |
| Contribution **margin (30 percent)**, **CAC** and the **shipping subsidy** come from other teams and were treated as exact | Q1, Q3 | the intervals do not include their uncertainty |
| The funnel is **observational** and the fix's effect is unknown | Q2 | a redesign may close only part of the gap |
| **12-month** LTV ignores what happens after month 12 and discounting | Q3 | paid may recover later; the ranking could soften |
| **Channels are not substitutable** | Q3 | moving paid budget to email will hit capacity limits |
| RFM segments depend on the **as-of date** and thresholds | Q4 | they must be rebuilt regularly |
| One year of behaviour; **seasonality** not separated | all | the holiday peak may distort recency and spend |
| **Synthetic data** | all | the data are built to illustrate; real data bring tracking errors, bots, returns and refunds |

### 6.4 The recommendation page

We use the one-page template and the linter of da.10 (reproduced in a compact form so that this chapter runs on its own): every number comes from the dictionaries computed above.

```python run
from dataclasses import dataclass, field
import re


@dataclass
class Finding:
    headline: str
    recommendations: list
    impact: str
    evidence: list
    confidence: str
    limitations: list
    next_steps: list

    def render_markdown(self):
        lines = ["# " + self.headline, "", "### Recommendation"]
        lines += [f"- **{r['action']}** (owner: {r['owner']}; by {r['by']})" for r in self.recommendations]
        lines += ["", "### Impact", self.impact, "", "### Evidence"] + [f"- {e}" for e in self.evidence]
        lines += ["", "### Confidence", self.confidence, "", "### Limitations"] + [f"- {l}" for l in self.limitations]
        lines += ["", "### Next steps"] + [f"- {n}" for n in self.next_steps]
        return "\n".join(lines)


def lint_finding(f, max_words=450):
    issues = []
    if not re.search(r"\d", f.headline):
        issues.append("headline has no number")
    for i, r in enumerate(f.recommendations):
        if not r.get("owner"):
            issues.append(f"recommendation {i + 1} has no owner")
        if not re.search(r"\d{1,2} \w+ \d{4}", str(r.get("by", ""))):
            issues.append(f"recommendation {i + 1} has no date")
    if not re.search(r"\d.*\b(to|between)\b.*\d", f.impact):
        issues.append("impact is a point, not a range")
    if len(f.evidence) < 2 or not all(re.search(r"\d", e) for e in f.evidence):
        issues.append("evidence needs at least two items, each with a number")
    if not any(re.search(r"CI|interval|range", e) for e in f.evidence):
        issues.append("no evidence item carries its uncertainty")
    if len(f.limitations) < 2:
        issues.append("fewer than two limitations")
    if not any(re.search(r"success|measure|within", n) for n in f.next_steps):
        issues.append("no success measure in the next steps")
    for phrase in ("monitor the situation", "further analysis", "look into", "it seems"):
        if phrase in f.render_markdown().lower():
            issues.append(f"vague phrase: {phrase!r}")
    if len(f.render_markdown().split()) > max_words:
        issues.append(f"too long for one page: {len(f.render_markdown().split())} words")
    return issues


finding = Finding(
    headline=(f"Fix mobile checkout first (worth {mob_lo / 1000:,.0f}k to {mob_hi / 1000:,.0f}k rupees of contribution a month), do not roll out the free-shipping banner yet, "
              f"and cut paid-ad spend: paid customers return {ltv.loc['paid', 'LTV12 / CAC']:.1f} times their acquisition cost in a year against {ltv.loc['organic', 'LTV12 / CAC']:.0f} to {ltv.loc['email', 'LTV12 / CAC']:.0f} elsewhere"),
    recommendations=[
        {"action": f"Redesign the mobile cart-to-checkout step and A/B test it (mobile converts {OPP['now_rate'] * 100:.0f}% of carts, desktop {OPP['desk_rate'] * 100:.0f}%)", "owner": "Head of Product", "by": "28 February 2025"},
        {"action": "Cap paid-ad spend at the current level and move the next increase to email and referral programmes", "owner": "Head of Marketing", "by": "31 January 2025"},
        {"action": "Hold the free-shipping banner; test a basket-threshold version with 37,000 visitors per group", "owner": "Head of Growth", "by": "31 March 2025"},
    ],
    impact=(f"The mobile fix could add {OPP['mid'] * gap_share[0]:,.0f} to {OPP['mid'] * gap_share[1]:,.0f} orders a month "
            f"({mob_lo / 1000:,.0f}k to {mob_hi / 1000:,.0f}k rupees of contribution) if it closes 30 to 100 percent of the gap. Each paid-acquired customer nets {paid_net:,.0f} rupees in 12 months, "
            f"each organic customer {org_net:,.0f}. The banner as designed is about break-even (range {AB['net_lo'] / 1000:+.0f}k to {AB['net_hi'] / 1000:+.0f}k a month)."),
    evidence=[
        f"Mobile sessions start checkout after adding to the cart {OPP['now_rate'] * 100:.0f}% of the time against {OPP['desk_rate'] * 100:.0f}% on desktop, in every channel (60,000 sessions in November 2024).",
        f"Email, referral and organic customers recover their acquisition cost on the first order; paid customers take about {int(payback['paid'])} months, and 12-month LTV/CAC is {ltv.loc['paid', 'LTV12 / CAC']:.1f} (95% CI {ltv.loc['paid', 'ratio CI low']:.1f} to {ltv.loc['paid', 'ratio CI high']:.1f}).",
        f"The banner test (12,000 visitors per group) found conversion {AB['conv_diff_pts']:+.2f} points (95% CI {AB['conv_lo']:+.2f} to {AB['conv_hi']:+.2f}) and revenue per visitor {AB['rpv']:+.1f} (CI {AB['rpv_lo']:+.1f} to {AB['rpv_hi']:+.1f}) against a break-even of {AB['breakeven_rpv']:.1f}.",
        f"RFM segments built in June predicted the next half-year: Champions spent {vt.loc['Champions', 'future spend per customer']:,.0f} per customer against {vt.loc['Hibernating', 'future spend per customer']:,.0f} for Hibernating customers."],
    confidence="High that the mobile gap and the paid-channel weakness are real (large effects, tight intervals). Low for the banner (underpowered test). The size of the mobile prize depends on how much of the gap a redesign can close.",
    limitations=["Margin (30%), CAC and the shipping subsidy are assumptions from other teams and are not in the intervals.",
                 "Twelve-month LTV ignores later purchases; paid customers may recover more after month 12.",
                 "The banner test was underpowered (about a third of the sample needed), so 'not significant' is not 'no effect'.",
                 "The data are synthetic and cover one year; seasonality is not separated."],
    next_steps=["Powered A/B test of the new mobile checkout, with the funnel gap as the minimum effect.",
                "Re-estimate LTV at 24 months when the 2023 cohorts allow.",
                "Success measure: mobile cart-to-checkout rate above 55% within three months of the redesign."])
print(finding.render_markdown())
print("\nwords:", len(finding.render_markdown().split()))
print("linter:", lint_finding(finding) or "no problems")
```
```text
# Fix mobile checkout first (worth 86k to 286k rupees of contribution a month), do not roll out the free-shipping banner yet, and cut paid-ad spend: paid customers return 1.3 times their acquisition cost in a year against 6 to 13 elsewhere

### Recommendation
- **Redesign the mobile cart-to-checkout step and A/B test it (mobile converts 45% of carts, desktop 65%)** (owner: Head of Product; by 28 February 2025)
- **Cap paid-ad spend at the current level and move the next increase to email and referral programmes** (owner: Head of Marketing; by 31 January 2025)
- **Hold the free-shipping banner; test a basket-threshold version with 37,000 visitors per group** (owner: Head of Growth; by 31 March 2025)

### Impact
The mobile fix could add 332 to 1,107 orders a month (86k to 286k rupees of contribution) if it closes 30 to 100 percent of the gap. Each paid-acquired customer nets 126 rupees in 12 months, each organic customer 732. The banner as designed is about break-even (range -140k to +109k a month).

### Evidence
- Mobile sessions start checkout after adding to the cart 45% of the time against 65% on desktop, in every channel (60,000 sessions in November 2024).
- Email, referral and organic customers recover their acquisition cost on the first order; paid customers take about 4 months, and 12-month LTV/CAC is 1.3 (95% CI 1.2 to 1.4).
- The banner test (12,000 visitors per group) found conversion +0.35 points (95% CI -0.28 to +0.98) and revenue per visitor +4.5 (CI -3.5 to +12.7) against a break-even of 5.6.
- RFM segments built in June predicted the next half-year: Champions spent 1,134 per customer against 195 for Hibernating customers.

### Confidence
High that the mobile gap and the paid-channel weakness are real (large effects, tight intervals). Low for the banner (underpowered test). The size of the mobile prize depends on how much of the gap a redesign can close.

### Limitations
- Margin (30%), CAC and the shipping subsidy are assumptions from other teams and are not in the intervals.
- Twelve-month LTV ignores later purchases; paid customers may recover more after month 12.
- The banner test was underpowered (about a third of the sample needed), so 'not significant' is not 'no effect'.
- The data are synthetic and cover one year; seasonality is not separated.

### Next steps
- Powered A/B test of the new mobile checkout, with the funnel gap as the minimum effect.
- Re-estimate LTV at 24 months when the 2023 cohorts allow.
- Success measure: mobile cart-to-checkout rate above 55% within three months of the redesign.

words: 434
linter: no problems
```

The page begins with the three actions in order of priority, names owners and dates, gives the size as a range, and lets each piece of evidence carry its interval and its source. The confidence line separates the strong conclusions from the weak one. The limitations are the ones of the table above. Read the headline aloud: a manager who stops there already knows what to do and why.

### 6.5 Presenting it

A meeting is not a report. Three habits make a recommendation land.

1. **Answer first.** Open with the recommendations and the one number behind each; give the analysis only when asked.
2. **Prepare for the three questions.** "How sure are you?" (the confidence line and an interval), "What would change your mind?" (name the assumption: "if the margin were 40 percent, the banner would pay"), "What do you need from me?" (an owner and a date).
3. **Separate the facts from the assumptions.** The mobile gap is a fact in the data. The size of the prize and the response to a win-back offer are assumptions until an experiment measures them. Say which is which.

Sensitivity to the key assumption can be shown in two lines, and it is the best answer to "what would change your mind?":

```python run
print("banner: net contribution a month (best estimate) for different margins and subsidies")
for margin in (0.25, 0.30, 0.40):
    row = []
    for sub in (15, 25, 40):
        c = conv_B * visitors_per_month * sub
        row.append(f"{gain_mid * margin - c:+10,.0f}")
    print(f"  margin {margin:.0%}: " + " | ".join(f"subsidy {s:>2}: {v}" for s, v in zip((15, 25, 40), row)))
```
```text
banner: net contribution a month (best estimate) for different margins and subsidies
  margin 25%: subsidy 15:     +6,389 | subsidy 25:    -27,824 | subsidy 40:    -79,142
  margin 30%: subsidy 15:    +17,930 | subsidy 25:    -16,282 | subsidy 40:    -67,601
  margin 40%: subsidy 15:    +41,013 | subsidy 25:     +6,801 | subsidy 40:    -44,518
```

At a 40 percent margin and a subsidy of 15 rupees the banner is clearly positive at the best estimate; at 25 percent and 40 rupees it loses a lot. The decision is sensitive to two assumptions that finance can pin down in a day, and it is better to say so than to let the manager discover it.

## 7. Project: a customer analytics case study

**The brief.** The head of growth wants a written case study on ShopNest's customers, ready for the quarterly review: the four questions answered, a recommendation with its limitations, and figures a non-analyst can read. Everything is generated from code so that it can be rebuilt next quarter, and every claim is checked.

### 7.1 Three figures

One figure for each of the questions that most need a picture: retention by channel (Q3), the mobile funnel gap (Q2), and the predictive power of the segments (Q4). The A/B result (Q1) is a table with intervals, so it needs no chart.

```python run
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pathlib, tempfile

_tmp = tempfile.TemporaryDirectory()
tmp = pathlib.Path(_tmp.name)
CH_COLOR = {"email": "#0072B2", "referral": "#009E73", "organic": "#E69F00", "paid": "#D55E00"}


def fig_retention():
    fig, ax = plt.subplots(figsize=(7.5, 4), layout="constrained")
    for ch in ["referral", "email", "organic", "paid"]:
        t = pooled_retention(ch, ks=tuple(range(1, 13)))
        ax.plot(t.index, t["retention %"], color=CH_COLOR[ch], linewidth=2, label=ch)
        ax.fill_between(t.index, t["CI low"], t["CI high"], color=CH_COLOR[ch], alpha=.15)
        ax.text(12.15, t["retention %"].iloc[-1] + {"email": 1.4, "organic": -1.4}.get(ch, 0), ch, color=CH_COLOR[ch], va="center", fontsize=9)
    ax.set_xlim(1, 13.5)
    ax.set_ylim(0, None)
    ax.set_xlabel("Months since the first order")
    ax.set_ylabel("Customers still buying (%)")
    ax.set_title("Referral customers keep buying longest; paid customers fade fastest", loc="left", fontweight="bold", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    return fig


def fig_funnel():
    st_ = step_rates(sessions, "device")
    steps = ["viewed %", "added %", "started %", "purchased %"]
    labels = ["view\nproduct", "add\nto cart", "start\ncheckout", "pay"]
    fig, ax = plt.subplots(figsize=(7.5, 4), layout="constrained")
    w = .38
    xs = np.arange(len(steps))
    for i, (dev, color) in enumerate((("desktop", "#0072B2"), ("mobile", "#D55E00"))):
        vals = st_.loc[dev, steps].to_numpy(float)
        b = ax.bar(xs + (i - .5) * w, vals, w, color=color, label=dev)
        ax.bar_label(b, labels=[f"{v:.0f}%" for v in vals], padding=2, fontsize=9)
    ax.set_xticks(xs, labels)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of the previous step (%)")
    ax.set_title("Mobile loses a fifth of its carts at the checkout step", loc="left", fontweight="bold", fontsize=11)
    ax.legend(frameon=False, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    return fig


def fig_rfm():
    v = vt.sort_values("future spend per customer")                     # lowest at the bottom, highest at the top
    fig, ax = plt.subplots(figsize=(7.5, 4), layout="constrained")
    ax.barh(v.index, v["future spend per customer"], color="#0072B2")
    ax.errorbar(v["future spend per customer"], range(len(v)), xerr=[v["future spend per customer"] - v["CI low"], v["CI high"] - v["future spend per customer"]], fmt="none", ecolor="black", capsize=3)
    ax.axvline(rfm_T["future_spend"].mean(), color="gray", linestyle="--")
    ax.text(rfm_T["future_spend"].mean() + 10, -0.45, "average", color="gray", fontsize=9)
    ax.set_xlabel("Spend in the following 6 months, per customer (rupees, 95% CI)")
    ax.set_title("Segments built in June predict spending in the next half-year", loc="left", fontweight="bold", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    return fig


for name, fn in (("retention", fig_retention), ("funnel", fig_funnel), ("rfm", fig_rfm)):
    f = fn()
    f.savefig(tmp / f"{name}.png", dpi=110)
    a = f.axes[0]
    print(f"{name:10} title: {a.get_title(loc='left')!r} | lines={len(a.lines)} patches={len(a.patches)}")
    plt.close(f)
```
```text
retention  title: 'Referral customers keep buying longest; paid customers fade fastest' | lines=4 patches=0
funnel     title: 'Mobile loses a fifth of its carts at the checkout step' | lines=0 patches=8
rfm        title: 'Segments built in June predict spending in the next half-year' | lines=3 patches=6
```

Titles state the finding, the interval bands and error bars show the uncertainty, and the retention chart labels the lines directly (da.09). We check each title against the numbers, as always:

```python run
t12 = {ch: pooled_retention(ch, ks=(12,)).loc[12, "retention %"] for ch in CH_COLOR}
print("retention at month 12:", {k: round(v, 1) for k, v in t12.items()}, "-> fastest fading is", min(t12, key=t12.get), "| best:", max(t12, key=t12.get))
sr = step_rates(sessions, "device")
print("mobile vs desktop cart->checkout:", round(sr.loc["mobile", "started %"], 1), "vs", round(sr.loc["desktop", "started %"], 1), "| mobile loses", round(sr.loc["desktop", "started %"] - sr.loc["mobile", "started %"], 0), "points more")
print("segments by future spend, highest first:", list(vt.sort_values("future spend per customer", ascending=False).index))
```
```text
retention at month 12: {'email': np.float64(11.4), 'referral': np.float64(18.4), 'organic': np.float64(10.6), 'paid': np.float64(3.4)} -> fastest fading is paid | best: referral
mobile vs desktop cart->checkout: 44.9 vs 65.2 | mobile loses 20.0 points more
segments by future spend, highest first: ['Champions', 'New / promising', 'Loyal', 'Needs attention', 'At risk', 'Hibernating']
```

### 7.2 Assemble the report and check it

```python run
import base64, html

CAPTIONS = {"retention": "Share of customers who place an order in each month after their first, pooled over cohorts with enough follow-up; bands are 95% intervals.",
            "funnel": "Share of sessions that reach each step, as a percentage of the previous step, November 2024 (60,000 sessions).",
            "rfm": "Segments built as of 30 June 2024 (RFM scores); bars show the average spend per customer in the following six months."}
ALTS = {"retention": "Four lines of the percentage of customers still buying over twelve months; referral and email stay highest, paid is lowest.",
        "funnel": "Grouped bars comparing desktop and mobile at four funnel steps; the two are equal except at the checkout step, where mobile is about 20 points lower.",
        "rfm": "Horizontal bars of future spend per customer for six segments, highest for Champions and lowest for Hibernating."}


def build_case_study(finding):
    p = ["<!doctype html><html lang='en'><head><meta charset='utf-8'><title>ShopNest customer analytics</title>",
         "<style>body{font-family:sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.5}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:.3rem .6rem;font-size:.9rem}figure{margin:1.5rem 0}img{max-width:100%}.box{background:#f4f4f4;padding:.8rem 1rem;border-radius:6px}</style></head><body>",
         f"<h1>{html.escape(finding.headline)}</h1><div class='box'><b>Recommendations</b><ul>"]
    p += [f"<li>{html.escape(r['action'])} <small>(owner: {html.escape(r['owner'])}; by {html.escape(r['by'])})</small></li>" for r in finding.recommendations]
    p += ["</ul></div>", f"<p><b>Impact.</b> {html.escape(finding.impact)}</p>", "<h2>The four questions</h2>", "<table><tr><th>Question</th><th>Finding</th><th>Size (with range)</th><th>Confidence</th></tr>"]
    p += ["<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>" for row in syn.itertuples(index=False)]
    p += ["</table>"]
    for name in ("funnel", "retention", "rfm"):
        b64 = base64.b64encode((tmp / f"{name}.png").read_bytes()).decode()
        p.append(f"<figure><img src='data:image/png;base64,{b64}' alt='{html.escape(ALTS[name], quote=True)}'><figcaption>{html.escape(CAPTIONS[name])}</figcaption></figure>")
    p += ["<h2>Evidence</h2><ul>"] + [f"<li>{html.escape(e)}</li>" for e in finding.evidence] + ["</ul>"]
    p += [f"<h2>Confidence</h2><p>{html.escape(finding.confidence)}</p><h2>Limitations</h2><ul>"] + [f"<li>{html.escape(l)}</li>" for l in finding.limitations] + ["</ul>"]
    p += ["<h2>Next steps</h2><ul>"] + [f"<li>{html.escape(n)}</li>" for n in finding.next_steps] + ["</ul>"]
    p += [f"<h2>Assumptions</h2><p>Contribution margin {MARGIN:.0%}; acquisition cost per customer {CAC}; shipping subsidy {SHIP_SUBSIDY} rupees per converted visitor in group B. Data: synthetic, orders to {ORD_END}.</p></body></html>"]
    return "\n".join(p)


ORD_END = str(orders["order_date"].max().date())
page = build_case_study(finding)
(tmp / "shopnest_case_study.html").write_text(page)
(tmp / "recommendation.md").write_text(finding.render_markdown())
print(f"written: {len(page) / 1024:.0f} KB (machine-specific) | {sorted(p.name for p in tmp.iterdir())}")
```
```text
written: 199 KB (machine-specific) | ['funnel.png', 'recommendation.md', 'retention.png', 'rfm.png', 'shopnest_case_study.html']
```

The last step is the test of the finished case study. It checks the things that go wrong in real reports: numbers that disagree between the text and the data, a missing figure, an unlinted recommendation, an interval that the text claims but the data do not support.

```python run
def check_case_study(page, finding):
    problems = []
    imgs = re.findall(r"<img [^>]*>", page)
    if len(imgs) != 3:
        problems.append(f"expected 3 figures, found {len(imgs)}")
    if not all(re.search(r"alt='[^']+'", t) for t in imgs):
        problems.append("a figure has no alt text")
    problems += [f"finding lint: {x}" for x in lint_finding(finding)]
    # the claims against the data
    if not (AB["conv_lo"] <= AB["conv_diff_pts"] <= AB["conv_hi"]):
        problems.append("the A/B estimate is outside its own interval")
    if AB["rpv_hi"] >= AB["breakeven_rpv"] and "do not roll out" not in finding.render_markdown().lower() and "hold the free-shipping banner" not in finding.render_markdown().lower():
        problems.append("the banner interval reaches break-even but the text does not hold the decision")
    if int(prof["customers"].sum()) != len(rfm):
        problems.append("RFM segments do not cover all customers")
    if abs(prof["% of revenue"].sum() - 100) > 1e-6:
        problems.append("segment revenue shares do not add to 100")
    if not (ltv["ratio CI low"] <= ltv["LTV12 / CAC"]).all() or not (ltv["LTV12 / CAC"] <= ltv["ratio CI high"]).all():
        problems.append("an LTV/CAC estimate is outside its interval")
    if f"{ltv.loc['paid', 'LTV12 / CAC']:.1f}" not in finding.render_markdown():
        problems.append("the paid LTV/CAC in the text does not match the table")
    return problems


print("case study check:", check_case_study(page, finding) or "no problems")
broken = Finding(headline="Some observations", recommendations=[{"action": "Look into mobile", "owner": "", "by": "soon"}], impact="Big.", evidence=["Mobile is bad"],
                 confidence="", limitations=["Data"], next_steps=["Further analysis"])
print("damaged copy:", check_case_study(page, broken))
```
```text
case study check: no problems
damaged copy: ['finding lint: headline has no number', 'finding lint: recommendation 1 has no owner', 'finding lint: recommendation 1 has no date', 'finding lint: impact is a point, not a range', 'finding lint: evidence needs at least two items, each with a number', 'finding lint: no evidence item carries its uncertainty', 'finding lint: fewer than two limitations', 'finding lint: no success measure in the next steps', "finding lint: vague phrase: 'further analysis'", "finding lint: vague phrase: 'look into'", 'the banner interval reaches break-even but the text does not hold the decision', 'the paid LTV/CAC in the text does not match the table']
```

All the checks pass on the real report, and the damaged copy trips the lint rules. A report that passes is not guaranteed to be right, but it cannot be wrong in the mechanical ways that waste a reviewer's time.

### 7.3 What to hand in

For a customer dataset of your own (a shop, an app, a subscription), deliver:

1. **The business questions**, one sentence each, with the decision behind each.
2. **An A/B test analysis** (or, without an experiment, an honest observational comparison with its limits): sample size or power, balance and SRM checks, the primary metric with its interval, guardrails, the decision against the break-even effect, and the sensitivity to the assumptions.
3. **A funnel** with segment cuts, a mix check, and the size of each leak with a range.
4. **A cohort retention table** that keeps immature cells empty, retention by channel with intervals, a 90-day repeat rate on eligible customers only, and a 12-month LTV with its payback against CAC.
5. **An RFM segmentation** with printed score ranges, validated on the future (holdout) with the gains curve, plus one alternative (k-means) with a stability check.
6. **A synthesis table** (answer, size as a range, confidence) and a **prioritised recommendation page** in the template of da.10 that passes the linter.
7. **Three figures** with finding titles and alt text, and **a test** that checks the claims against the data.
8. **An assumptions and limitations list** that names who owns each assumption.

## 8. Common traps

| Trap | What happens | Fix |
|---|---|---|
| No sample size before the test | an underpowered test that cannot decide | power calculation from the minimum effect that pays (2.2) |
| Stopping at the first significant day | about one A/A test in five "wins" | fixed horizon or sequential methods (2.8) |
| Skipping the sample ratio check | an invalid experiment analysed | SRM check first; debug, do not analyse (2.4) |
| "Not significant" read as "no effect" | a good idea dropped | read the interval against the break-even effect (2.5, 2.12) |
| Counting revenue as profit | a banner that loses money looks like a win | contribution margin and the subsidy cost (2.11) |
| Segment results as findings | false discoveries | interaction test; segments as hypotheses (2.10) |
| Funnel from events, not sessions | steps too big, rates too small | count the unit the question names (3.1) |
| Channel effect that is really a device effect | the wrong fix | cross-tabs and mix checks (3.4) |
| Treating the opportunity ceiling as a forecast | an inflated promise | assume a share of the gap; give a range (3.5) |
| Zeros for months that have not happened | a fake cliff in the retention matrix | keep immature cells empty (4.2) |
| Repeat rate over everyone | recent customers pull it down | only customers observed long enough (4.4) |
| Revenue LTV without acquisition cost | the best revenue channel can lose money | LTV/CAC and payback (4.5) |
| LTV beyond the data | speculation as a number | state the horizon; use the observed one (4.5) |
| `qcut` on tied variables | errors or arbitrary scores | hand-made bins for tied variables (5.2) |
| Segments never validated | pretty picture, no predictive value | holdout test and gains curve (5.4) |
| Unstable clusters named as segments | the groups change with each run | several initialisations, stability index (5.5) |
| Actions without a test | response rates assumed, not measured | each segment action has an A/B plan (5.6) |
| Four findings, equally confident | the reader cannot tell the solid from the weak | a synthesis table with size, range, confidence (6.1) |
| Hidden assumptions | the recommendation collapses when finance disagrees | a limitations table; a sensitivity check (6.3, 6.5) |

A habit for every recommendation: write down the one assumption that, if wrong, would reverse it; then show the reader how sensitive the answer is to it.

## 9. Summary

- **A/B testing**: hypothesis, one primary metric with guardrails, the unit of randomisation, a **power calculation** from the minimum effect that pays (`n = 2(z_a + z_b)^2 p(1-p) / d^2`), a **sample ratio check** and balance checks before any analysis, the effect with its interval, **revenue per visitor** with a bootstrap, and the decision against the **break-even** effect (extra revenue times margin must exceed the cost). **CUPED** narrows intervals by `sqrt(1 - rho^2)`, useful only when the pre-period variable is strongly correlated. **Peeking** inflates false positives to about 21 percent; novelty effects, segments and many metrics need care; an **underpowered** test mostly returns "inconclusive" even for a real effect (57 percent significant in our repeats, 8 percent clear of the threshold).
- **Funnels**: count sessions (or users), require nested steps, keep everyone who entered, read both the step rate and the absolute drop, cut by segment and check the **mix** with cross-tabs, then **size** each leak (a ceiling, with a range) and rank the fixes. A funnel says where to look; an experiment says whether a fix works.
- **Cohorts and retention**: cohort by first-order month; retention as distinct active customers over cohort size; **mature cells only**; pool curves by adding numerators and denominators; the **90-day repeat rate** on eligible customers; **LTV** over a fixed horizon among customers observed that long; **LTV/CAC** and **payback** to decide where acquisition money goes; stable cohort quality as a result in itself.
- **RFM**: recency, frequency and monetary value as of a **stated date**; scores by quantiles for continuous variables and **hand-made bins for tied ones**; rule-based segments that are mutually exclusive and exhaustive; **validate on the future** (holdout spend and the gains curve); k-means as a data-driven check with a stability test; every segment gets an action, a metric and a way to test it.
- **From analyses to a recommendation**: a synthesis table with the finding, the size as a range and the confidence; prioritisation by impact, confidence and effort; an explicit **limitations** table with owners; a sensitivity check on the assumption that matters most; one page generated from the numbers and checked by the linter.
- **The case study** is code: three finding-titled figures with alt text, an HTML report, and tests that check the claims against the data.

You reached the outcome of this chapter: you can **run a full customer analysis and present recommendations with their limitations**. ShopNest's four questions ended with an ordered plan: fix the mobile checkout (the gap is certain, the prize a range), hold the free-shipping banner (an honest test that cannot show it pays), cut paid-ad spend (each paid customer nets a fraction of the others), and treat win-back as a small bet; each with owners, dates, ranges and the doubts that could change it. Next, da.12 moves to Excel, because many analyses must also live in a spreadsheet: PivotTables, lookups, conditional aggregation and Power Query, with the discipline of matching the pandas numbers exactly.
